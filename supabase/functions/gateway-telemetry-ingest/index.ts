import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

console.log("Hello from gateway-telemetry-ingest!")

serve(async (req) => {
    const { method } = req

    // Health check
    if (method === 'GET') {
        return new Response(JSON.stringify({ status: 'active' }), {
            headers: { 'Content-Type': 'application/json' },
        })
    }

    if (method !== 'POST') {
        return new Response('Method not allowed', { status: 405 })
    }

    try {
        const payload = await req.json()
        const apiKey = req.headers.get('X-Gateway-Key')

        // Basic API Key check
        const expectedKey = Deno.env.get('GATEWAY_API_KEY')
        if (expectedKey && apiKey !== expectedKey) {
            return new Response('Unauthorized', { status: 401 })
        }

        // Initialize Supabase Client
        const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
        const supabase = createClient(supabaseUrl, supabaseKey)

        // Log to telemetry_events
        const { error } = await supabase
            .from('telemetry_events')
            .insert({
                event_type: payload.event_type || 'gateway_pulse',
                source: payload.source || 'Unknown Gateway',
                payload: payload
            })

        if (error) {
            console.error('Error logging to Supabase:', error)
            return new Response(JSON.stringify({ error: error.message }), { status: 500 })
        }

        return new Response(JSON.stringify({ message: 'Telemetry received' }), {
            headers: { 'Content-Type': 'application/json' },
            status: 200,
        })

    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            headers: { 'Content-Type': 'application/json' },
            status: 400,
        })
    }
})
