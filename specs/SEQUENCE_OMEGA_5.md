# Sequence Ω.5: TEMPORAL COHERENCE & DRIFT-LOCK

## 1. DATABASE MIGRATION (SQL)
**Path:** `spiral_supabase/migrations/20251129_seq_omega5_temporal_drift.sql`

```sql
-- Sequence Ω.5: Temporal Coherence & Drift-Lock

-- 1. Temporal Drift Log Table
CREATE TABLE IF NOT EXISTS temporal_drift_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    anchor_timestamp TIMESTAMPTZ NOT NULL,
    drift_delta_ms INTEGER, -- Nullable if just an anchor
    phase_lock_hash TEXT,
    severity TEXT CHECK (severity IN ('GREEN', 'YELLOW', 'RED')),
    source TEXT NOT NULL
);

-- 2. Record Anchor Function
CREATE OR REPLACE FUNCTION fn_record_temporal_anchor(
    p_source TEXT,
    p_timestamp TIMESTAMPTZ DEFAULT now()
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_phase_lock_hash TEXT;
    v_id UUID;
BEGIN
    -- Capture Phase Lock Hash
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    INSERT INTO temporal_drift_log (anchor_timestamp, phase_lock_hash, severity, source)
    VALUES (p_timestamp, v_phase_lock_hash, 'GREEN', p_source)
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

-- 3. Verify Drift Function
CREATE OR REPLACE FUNCTION fn_verify_temporal_drift(
    p_client_timestamp TIMESTAMPTZ,
    p_source TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_server_time TIMESTAMPTZ := now();
    v_delta_ms INTEGER;
    v_severity TEXT;
    v_phase_lock_hash TEXT;
    v_id UUID;
BEGIN
    -- Calculate Delta (Client - Server)
    v_delta_ms := EXTRACT(EPOCH FROM (p_client_timestamp - v_server_time)) * 1000;

    -- Determine Severity
    IF ABS(v_delta_ms) < 1000 THEN
        v_severity := 'GREEN';
    ELSIF ABS(v_delta_ms) < 5000 THEN
        v_severity := 'YELLOW';
    ELSE
        v_severity := 'RED';
    END IF;

    -- Capture Phase Lock Hash
    BEGIN
        SELECT hash INTO v_phase_lock_hash FROM fn_verify_phase_lock();
    EXCEPTION WHEN OTHERS THEN
        v_phase_lock_hash := NULL;
    END;

    -- Log Entry
    INSERT INTO temporal_drift_log (anchor_timestamp, drift_delta_ms, phase_lock_hash, severity, source)
    VALUES (p_client_timestamp, v_delta_ms, v_phase_lock_hash, v_severity, p_source)
    RETURNING id INTO v_id;

    RETURN jsonb_build_object(
        'id', v_id,
        'server_time', v_server_time,
        'delta_ms', v_delta_ms,
        'severity', v_severity,
        'phase_lock_hash', v_phase_lock_hash
    );
END;
$$;

-- 4. Temporal Drift Status View
CREATE OR REPLACE VIEW view_temporal_drift_status AS
SELECT
    id,
    created_at,
    anchor_timestamp,
    drift_delta_ms,
    phase_lock_hash,
    severity,
    source
FROM temporal_drift_log
ORDER BY created_at DESC
LIMIT 50;
```

## 2. RUNTIME INTEGRATION (PYTHON)

### Core Temporal Engine
**Path:** `core/temporal.py` (New Module)

```python
from datetime import datetime, timezone
from typing import Dict, Any
from .db import db

class TemporalDriftEngine:
    """
    Manages temporal coherence and drift detection.
    """
    def __init__(self):
        self.db = db

    def record_anchor(self, source: str = "System") -> str:
        """
        Records a temporal anchor point.
        """
        try:
            res = self.db.client._ensure_client().rpc("fn_record_temporal_anchor", {
                "p_source": source,
                "p_timestamp": datetime.now(timezone.utc).isoformat()
            }).execute()
            return res.data
        except Exception as e:
            print(f"[TEMPORAL] Anchor failed: {e}")
            return None

    def verify_drift(self, source: str = "System") -> Dict[str, Any]:
        """
        Verifies temporal drift against the server.
        """
        try:
            res = self.db.client._ensure_client().rpc("fn_verify_temporal_drift", {
                "p_client_timestamp": datetime.now(timezone.utc).isoformat(),
                "p_source": source
            }).execute()
            return res.data
        except Exception as e:
            print(f"[TEMPORAL] Drift check failed: {e}")
            return {"error": str(e)}
```

### Module Updates

**Path:** `core/status_api.py`

```python
# ... imports ...
from .temporal import TemporalDriftEngine # [NEW]

class StatusAPI:
    def __init__(self, db=None):
        self.db = db or default_db
        self.temporal = TemporalDriftEngine() # [NEW]

    def get_status(self) -> Dict[str, Any]:
        # ... existing emit_audit_event ...
        
        # [NEW] Record Temporal Anchor
        self.temporal.record_anchor(source="StatusAPI")
        
        # ... existing logic ...
```

**Path:** `core/guardian/runner.py`

```python
# ... imports ...
from core.temporal import TemporalDriftEngine # [NEW]

class GuardianRunner:
    def __init__(self):
        # ... existing ...
        self.temporal = TemporalDriftEngine() # [NEW]

    def tick(self):
        # ... existing emit_audit_event ...
        
        # [NEW] Verify Drift
        drift_status = self.temporal.verify_drift(source="GuardianRunner")
        if drift_status.get("severity") == "RED":
            print(f"[TEMPORAL] CRITICAL DRIFT DETECTED: {drift_status.get('delta_ms')}ms")
            # Could trigger emergency lock here
            
        # ... existing logic ...
```

**Path:** `core/scarlock.py`

```python
# ... imports ...
from .temporal import TemporalDriftEngine # [NEW]

class ScarLock:
    def __init__(self, db=None):
        # ... existing ...
        self.temporal = TemporalDriftEngine() # [NEW]

    def engage_lock(self, reason: str, actor: str = "guardian") -> None:
        # [NEW] Check drift before engaging (optional safety check, or just log it)
        self.temporal.verify_drift(source="ScarLock")
        
        # ... existing logic ...
```

## 3. DASHBOARD LAYER (NEXT.JS)

**Path:** `web/dashboard/hooks/useTemporalDrift.ts`

```typescript
import { useState, useEffect } from 'react';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;
const supabase = createClient(supabaseUrl, supabaseKey);

export interface DriftEntry {
  id: string;
  created_at: string;
  anchor_timestamp: string;
  drift_delta_ms: number | null;
  phase_lock_hash: string | null;
  severity: 'GREEN' | 'YELLOW' | 'RED';
  source: string;
}

export function useTemporalDrift() {
  const [entries, setEntries] = useState<DriftEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDrift = async () => {
      const { data, error } = await supabase
        .from('view_temporal_drift_status')
        .select('*');
      
      if (data) {
        setEntries(data);
      }
      setLoading(false);
    };

    fetchDrift();
    const interval = setInterval(fetchDrift, 3000); // Poll every 3s
    return () => clearInterval(interval);
  }, []);

  return { entries, loading };
}
```

**Path:** `web/dashboard/app/temporal/page.tsx`

```tsx
'use client';

import React from 'react';
import { useTemporalDrift, DriftEntry } from '../../hooks/useTemporalDrift';

export default function TemporalPage() {
  const { entries, loading } = useTemporalDrift();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'GREEN': return 'text-green-500 border-green-800';
      case 'YELLOW': return 'text-yellow-500 border-yellow-800';
      case 'RED': return 'text-red-500 border-red-800';
      default: return 'text-gray-500 border-gray-800';
    }
  };

  return (
    <div className="p-8 bg-black min-h-screen text-green-500 font-mono">
      <h1 className="text-3xl mb-6 border-b border-green-800 pb-2">Ω.5 TEMPORAL COHERENCE</h1>
      
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-gray-900 border border-green-900 p-4 rounded">
          <h2 className="text-xl mb-4">Drift Log</h2>
          {loading ? (
            <div>Synchronizing Chronometers...</div>
          ) : (
            <div className="space-y-2">
              <div className="grid grid-cols-6 text-xs text-gray-400 border-b border-gray-800 pb-2 mb-2">
                <div className="col-span-1">TIME (UTC)</div>
                <div className="col-span-1">SOURCE</div>
                <div className="col-span-1">DELTA (ms)</div>
                <div className="col-span-1">SEVERITY</div>
                <div className="col-span-2">PHASE HASH</div>
              </div>
              {entries.map((entry) => (
                <div key={entry.id} className={`grid grid-cols-6 text-sm py-1 border-b border-gray-800/50 ${getSeverityColor(entry.severity)}`}>
                  <div className="col-span-1 truncate">{new Date(entry.created_at).toLocaleTimeString()}</div>
                  <div className="col-span-1">{entry.source}</div>
                  <div className="col-span-1">{entry.drift_delta_ms !== null ? `${entry.drift_delta_ms}ms` : '-'}</div>
                  <div className="col-span-1 font-bold">{entry.severity}</div>
                  <div className="col-span-2 font-mono text-xs text-gray-500 truncate">{entry.phase_lock_hash || 'NULL'}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

## 4. CLI EXTENSIONS
**Path:** `scripts/spiralctl.py`

```python
# ... imports ...
from core.temporal import TemporalDriftEngine # [NEW]

# ... inside main/subparsers ...

    # Temporal Command
    temporal_parser = subparsers.add_parser("temporal", help="Temporal Coherence commands")
    temporal_sub = temporal_parser.add_subparsers(dest="temporal_cmd")

    temporal_sub.add_parser("anchor", help="Manually record an anchor")
    temporal_sub.add_parser("verify", help="Run drift-check manually")
    temporal_sub.add_parser("log", help="Fetch recent drift entries")

# ... inside command handlers ...

def cmd_temporal(args):
    engine = TemporalDriftEngine()
    
    if args.temporal_cmd == "anchor":
        id = engine.record_anchor(source="CLI")
        print(f"[TEMPORAL] Anchor recorded: {id}")
        
    elif args.temporal_cmd == "verify":
        res = engine.verify_drift(source="CLI")
        print(f"[TEMPORAL] Drift Check: {res}")
        
    elif args.temporal_cmd == "log":
        try:
            res = db.client._ensure_client().table("view_temporal_drift_status").select("*").limit(10).execute()
            for row in res.data:
                print(f"[{row['created_at']}] {row['source']} | Delta: {row['drift_delta_ms']}ms | {row['severity']}")
        except Exception as e:
            print(f"Error fetching log: {e}")
```
