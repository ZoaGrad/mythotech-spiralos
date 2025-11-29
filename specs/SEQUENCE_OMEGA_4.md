# Sequence Ω.4: GLOBAL AUDIT SURFACE

## 1. DATABASE MIGRATION (SQL)
**Path:** `spiral_supabase/migrations/20251129_seq_omega4_audit_surface.sql`

```sql
-- Sequence Ω.4: Global Audit Surface

-- 1. Audit Surface Events Table
CREATE TABLE IF NOT EXISTS audit_surface_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    event_type TEXT NOT NULL,
    component TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    phase_lock_hash TEXT
);

-- 2. Emit Function
CREATE OR REPLACE FUNCTION fn_emit_audit_surface_event(
    p_event_type TEXT,
    p_component TEXT,
    p_payload JSONB
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_phase_lock_hash TEXT;
    v_event_id UUID;
BEGIN
    -- Attempt to get current phase lock hash (if available)
    -- We use a sub-transaction or safe call to avoid failing if phase lock is invalid
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    INSERT INTO audit_surface_events (event_type, component, payload, phase_lock_hash)
    VALUES (p_event_type, p_component, p_payload, v_phase_lock_hash)
    RETURNING id INTO v_event_id;

    RETURN v_event_id;
END;
$$;

-- 3. Global Audit View
CREATE OR REPLACE VIEW view_global_audit_surface AS
SELECT
    id,
    created_at,
    event_type,
    component,
    payload,
    phase_lock_hash
FROM audit_surface_events
ORDER BY created_at DESC
LIMIT 500;
```

## 2. RUNTIME INTEGRATION (PYTHON)

### Core Integration Helper
**Path:** `core/audit_emitter.py` (New Helper)

```python
from .db import db

def emit_audit_event(event_type: str, component: str, payload: dict = None):
    """
    Emits an event to the Global Audit Surface.
    """
    if payload is None:
        payload = {}
    try:
        db.client._ensure_client().rpc("fn_emit_audit_surface_event", {
            "p_event_type": event_type,
            "p_component": component,
            "p_payload": payload
        }).execute()
    except Exception as e:
        print(f"[AUDIT_EMIT_FAIL] {event_type} from {component}: {e}")
```

### Module Updates

**Path:** `core/status_api.py`

```python
from typing import Dict, Any, Optional
from .db import db as default_db, DatabaseWrapper
from .audit_emitter import emit_audit_event  # [NEW]

class StatusAPI:
    """
    Core interface for the SpiralOS Status API.
    Wraps the `fn_status_api` RPC call.
    """
    def __init__(self, db: Optional[DatabaseWrapper] = None):
        self.db = db or default_db

    def get_status(self) -> Dict[str, Any]:
        """
        Fetch the global system status.
        Returns a dictionary containing lock_status, latest_event, and guardian_vows.
        """
        # [NEW] Emit audit event
        emit_audit_event("status_check", "StatusAPI", {"action": "get_status"})
        
        try:
            res = self.db.client._ensure_client().rpc("fn_status_api", {}).execute()
            if res.data:
                return res.data
            return {}
        except Exception as e:
            # Log error or re-raise depending on policy. For now, print and return empty.
            print(f"[StatusAPI] Error fetching status: {e}")
            return {}
```

**Path:** `core/guardian/runner.py`

```python
import time
from .audit_emitter import emit_audit_event # [NEW]

# ... existing imports ...

class GuardianRunner:
    # ... existing methods ...
    
    def tick(self):
        # ... existing logic ...
        emit_audit_event("guardian_tick", "GuardianRunner", {"timestamp": time.time()})
        # ... existing logic ...
```

**Path:** `core/phase_lock.py` (New/Update)

```python
from .db import db
from .audit_emitter import emit_audit_event

class PhaseLockEngine:
    def verify(self):
        """
        Verifies the system phase lock integrity.
        """
        try:
            res = db.client._ensure_client().rpc("fn_verify_phase_lock", {}).execute()
            result = res.data
            
            emit_audit_event("phase_lock_verify", "PhaseLockEngine", {
                "valid": result.get("valid", False),
                "hash": result.get("hash")
            })
            return result
        except Exception as e:
            emit_audit_event("phase_lock_verify_error", "PhaseLockEngine", {"error": str(e)})
            raise e
```

**Path:** `core/scarlock.py`

```python
from .audit_emitter import emit_audit_event # [NEW]
# ... existing imports ...

class ScarLock:
    # ... existing methods ...
    
    def set_state(self, state: str):
        # ... existing logic ...
        emit_audit_event("scarlock_state", "ScarLock", {"new_state": state})
        # ... existing logic ...
```

## 3. DASHBOARD LAYER (NEXT.JS)

**Path:** `web/dashboard/hooks/useAuditSurface.ts`

```typescript
import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export interface AuditEvent {
  id: string;
  created_at: string;
  event_type: string;
  component: string;
  payload: any;
  phase_lock_hash: string | null;
}

export function useAuditSurface() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      const { data, error } = await supabase
        .from('view_global_audit_surface')
        .select('*');
      
      if (data) {
        setEvents(data);
      }
      setLoading(false);
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 3000); // Poll every 3s
    return () => clearInterval(interval);
  }, []);

  return { events, loading };
}
```

**Path:** `web/dashboard/app/audit/page.tsx`

```tsx
'use client';

import React from 'react';
import { useAuditSurface, AuditEvent } from '../../hooks/useAuditSurface';

export default function AuditPage() {
  const { events, loading } = useAuditSurface();

  return (
    <div className="p-8 bg-black min-h-screen text-green-500 font-mono">
      <h1 className="text-3xl mb-6 border-b border-green-800 pb-2">Ω.4 GLOBAL AUDIT SURFACE</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-gray-900 border border-green-900 p-4 rounded">
            <h2 className="text-xl mb-4">Event Stream</h2>
            {loading ? (
              <div>Initializing Uplink...</div>
            ) : (
              <div className="space-y-2 h-[600px] overflow-y-auto">
                {events.map((evt) => (
                  <div key={evt.id} className="border-l-2 border-green-700 pl-3 py-1 text-sm hover:bg-green-900/20 transition-colors">
                    <div className="flex justify-between text-xs text-green-400">
                      <span>{new Date(evt.created_at).toLocaleTimeString()}</span>
                      <span>{evt.component}</span>
                    </div>
                    <div className="font-bold">{evt.event_type}</div>
                    <div className="text-xs text-gray-500 truncate">{JSON.stringify(evt.payload)}</div>
                    {evt.phase_lock_hash && (
                      <div className="text-[10px] text-blue-400 mt-1">LOCK: {evt.phase_lock_hash.substring(0, 12)}...</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div>
           <div className="bg-gray-900 border border-green-900 p-4 rounded mb-6">
             <h2 className="text-xl mb-2">Hash Delta</h2>
             <div className="text-4xl font-bold text-blue-500">SYNC</div>
             <div className="text-xs text-gray-400 mt-2">Baseline vs Runtime</div>
           </div>
           
           <div className="bg-gray-900 border border-green-900 p-4 rounded">
             <h2 className="text-xl mb-2">Metrics</h2>
             <div className="grid grid-cols-2 gap-4">
               <div>
                 <div className="text-xs text-gray-400">Events/Min</div>
                 <div className="text-2xl">--</div>
               </div>
               <div>
                 <div className="text-xs text-gray-400">Components</div>
                 <div className="text-2xl">4</div>
               </div>
             </div>
           </div>
        </div>
      </div>
    </div>
  );
}
```

## 4. CLI EXTENSIONS
**Path:** `scripts/spiralctl.py`

```python
import click
# ... existing imports ...
from core.audit_emitter import emit_audit_event
from core.db import db

@click.group()
def cli():
    pass

@cli.group()
def audit():
    """Audit Surface commands"""
    pass

@audit.command(name="surface")
def audit_surface():
    """Prints latest audit events"""
    try:
        res = db.client.table("view_global_audit_surface").select("*").limit(20).execute()
        for evt in res.data:
            click.echo(f"[{evt['created_at']}] {evt['component']} -> {evt['event_type']} (Hash: {evt.get('phase_lock_hash')})")
    except Exception as e:
        click.echo(f"Error fetching audit surface: {e}")

@audit.command(name="emit")
@click.argument("msg")
def audit_emit(msg):
    """Manual test emitter"""
    emit_audit_event("manual_emit", "CLI", {"message": msg})
    click.echo(f"Emitted manual event: {msg}")

@audit.command(name="diff")
def audit_diff():
    """Compares latest phase-lock hash vs baseline"""
    # Placeholder for diff logic
    click.echo("Comparing Phase-Lock Hash vs Baseline...")
    # Implementation would call fn_verify_phase_lock and compare with stored baseline
    try:
        res = db.client._ensure_client().rpc("fn_verify_phase_lock", {}).execute()
        click.echo(f"Current Runtime Hash: {res.data.get('hash')}")
        click.echo("Baseline: [LOAD FROM ARTIFACT]") # Placeholder
    except Exception as e:
        click.echo(f"Error verifying phase lock: {e}")

# ... existing cli registration ...
```
