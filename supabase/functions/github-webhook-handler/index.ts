import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

console.log("Hello from github-webhook-handler!")

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
        const eventType = req.headers.get('X-GitHub-Event') || 'unknown'
        const signature = req.headers.get('X-Hub-Signature-256')

        // Verify signature (TODO: Implement actual HMAC verification with secret)
        // const secret = Deno.env.get('GITHUB_WEBHOOK_SECRET')
        // if (!verifySignature(payload, signature, secret)) {
        //   return new Response('Unauthorized', { status: 401 })
        // }

        // Initialize Supabase Client
        const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
        const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
        const supabase = createClient(supabaseUrl, supabaseKey)

        // Log to telemetry_events
        const { error } = await supabase
            .from('telemetry_events')
            .insert({
                event_type: `github_${eventType}`,
                source: 'GitHub',
                payload: payload
            })

        if (error) {
            console.error('Error logging to Supabase:', error)
            return new Response(JSON.stringify({ error: error.message }), { status: 500 })
        }

        return new Response(JSON.stringify({ message: 'Event received' }), {
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
