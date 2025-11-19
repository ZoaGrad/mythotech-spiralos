// PanicFrame Edge Function
// Description:
//  - Receives webhook/events from PanicFrame and records them in Supabase.
//  - Validates a shared secret header: x-panicframe-secret
//  - Inserts into table: panicframe_signals (id uuid default gen_random_uuid(), created_at timestamptz default now(), level text, key text, meta jsonb)
//
// Deployment:
//  supabase functions deploy panicframe-edge-fn --no-verify-jwt
//  supabase functions secrets set PANICFRAME_WEBHOOK_SECRET=... SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=...
//
// Local test (via Supabase CLI):
//  supabase functions serve panicframe-edge-fn --no-verify-jwt
//  curl -X POST 'http://localhost:54321/functions/v1/panicframe-edge-fn' \
//       -H 'Content-Type: application/json' \
//       -H 'x-panicframe-secret: YOUR_SECRET' \
//       -d '{"level":"warn","key":"sensor.overload","meta":{"source":"unit-7","value":87}}'
//
// Notes:
// - Use service role key for writes from Edge Functions where RLS applies.
// - Ensure RLS policies allow the service role to insert into panicframe_signals.

import 'jsr:@supabase/functions-js/edge-runtime.d.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
const PANICFRAME_WEBHOOK_SECRET = Deno.env.get('PANICFRAME_WEBHOOK_SECRET')

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

Deno.serve(async (req: Request) => {
  try {
    if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      return jsonResponse({ error: 'Server misconfigured: missing SUPABASE env' }, 500)
    }

    const secret = req.headers.get('x-panicframe-secret')
    if (!secret || secret !== PANICFRAME_WEBHOOK_SECRET) {
      return jsonResponse({ error: 'Unauthorized' }, 401)
    }

    if (req.method !== 'POST') {
      return jsonResponse({ error: 'Method not allowed' }, 405)
    }

    const payload = await req.json().catch(() => null)
    if (!payload || typeof payload !== 'object') {
      return jsonResponse({ error: 'Invalid JSON' }, 400)
    }

    const level = (payload as any).level ?? 'info'
    const key = (payload as any).key ?? 'unknown'
    const meta = (payload as any).meta ?? {}

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    const { error } = await supabase
      .from('panicframe_signals')
      .insert([{ level, key, meta }])

    if (error) {
      console.error('Insert error:', error)
      return jsonResponse({ error: 'Failed to persist signal' }, 500)
    }

    return jsonResponse({ status: 'accepted' }, 202)
  } catch (err) {
    console.error('Unhandled error:', err)
    return jsonResponse({ error: 'Internal error' }, 500)
  }
})
