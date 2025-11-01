// SpiralOS GitHub Webhook Edge Function
// Ingests GitHub events and converts them to Ache measurements
// ΔΩ.126.0 - Constitutional Cognitive Sovereignty

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-github-event, x-hub-signature-256',
}

interface GitHubCommit {
  id: string
  message: string
  author: {
    name: string
    email: string
  }
  added: string[]
  removed: string[]
  modified: string[]
}

interface GitHubIssue {
  number: number
  title: string
  body: string
  state: string
  labels: Array<{ name: string }>
}

interface WebhookPayload {
  commits?: GitHubCommit[]
  issue?: GitHubIssue
  action?: string
  repository?: {
    full_name: string
  }
}

/**
 * Calculate Ache level from GitHub commit
 * Higher ache = more entropy/incoherence
 */
function computeAcheFromCommit(commit: GitHubCommit): number {
  const totalChanges = (commit.added?.length || 0) + 
                      (commit.removed?.length || 0) + 
                      (commit.modified?.length || 0)
  
  // More changes = higher initial ache (needs more coherence work)
  // Normalize to [0, 1] range (assume max 20 files changed)
  const changeAche = Math.min(totalChanges / 20, 0.8)
  
  // Message quality affects ache (poor messages = higher ache)
  const messageLength = commit.message?.length || 0
  const messageQuality = messageLength > 50 ? 0.1 : 0.3
  
  return Math.min(changeAche + messageQuality, 1.0)
}

/**
 * Calculate Ache level from GitHub issue using NLP heuristics
 */
function nlpAcheScore(text: string): number {
  if (!text) return 0.7 // High ache for empty issues
  
  // Negative sentiment indicators increase ache
  const negativeWords = ['bug', 'error', 'fail', 'broken', 'crash', 'issue', 'problem']
  const negativeCount = negativeWords.filter(word => 
    text.toLowerCase().includes(word)
  ).length
  
  // Well-structured issues have lower ache
  const hasCodeBlocks = text.includes('```')
  const hasSteps = text.includes('Step') || text.includes('1.')
  const structure = (hasCodeBlocks ? -0.1 : 0) + (hasSteps ? -0.1 : 0)
  
  // Calculate ache
  const baseAche = 0.5
  const sentimentAche = Math.min(negativeCount * 0.1, 0.3)
  
  return Math.max(0.1, Math.min(baseAche + sentimentAche + structure, 1.0))
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Get Supabase client
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    // Parse webhook
    const eventType = req.headers.get('x-github-event')
    const payload: WebhookPayload = await req.json()

    console.log(`Received GitHub webhook: ${eventType}`)

    // Store webhook for audit
    const { data: webhookRecord, error: webhookError } = await supabase
      .from('github_webhooks')
      .insert({
        event_type: eventType,
        payload: payload,
        processed: false
      })
      .select()
      .single()

    if (webhookError) {
      console.error('Failed to store webhook:', webhookError)
      throw webhookError
    }

    let acheEventId: string | null = null

    // Process based on event type
    if (eventType === 'push' && payload.commits && payload.commits.length > 0) {
      // Process commits
      for (const commit of payload.commits) {
        const acheLevel = computeAcheFromCommit(commit)
        
        // Create Ache event
        const { data: acheEvent, error: acheError } = await supabase
          .from('ache_events')
          .insert({
            source: 'github_commit',
            source_id: commit.id,
            content: {
              commit_id: commit.id,
              message: commit.message,
              author: commit.author,
              changes: {
                added: commit.added?.length || 0,
                removed: commit.removed?.length || 0,
                modified: commit.modified?.length || 0
              },
              repository: payload.repository?.full_name
            },
            ache_level: acheLevel
          })
          .select()
          .single()

        if (acheError) {
          console.error('Failed to create ache event for commit:', acheError)
          continue
        }

        acheEventId = acheEvent.id
        console.log(`Created ache event ${acheEventId} for commit ${commit.id} (ache: ${acheLevel})`)

        // Trigger ScarIndex calculation
        const { data: calculation, error: calcError } = await supabase
          .rpc('coherence_calculation', { event_id: acheEventId })

        if (calcError) {
          console.error('Failed to calculate ScarIndex:', calcError)
        } else {
          console.log(`ScarIndex calculated: ${calculation?.scarindex}`)
        }
      }
    } else if (eventType === 'issues' && payload.action === 'opened' && payload.issue) {
      // Process new issue
      const issue = payload.issue
      const acheLevel = nlpAcheScore(issue.body)
      
      // Create Ache event
      const { data: acheEvent, error: acheError } = await supabase
        .from('ache_events')
        .insert({
          source: 'github_issue',
          source_id: `issue_${issue.number}`,
          content: {
            number: issue.number,
            title: issue.title,
            body: issue.body,
            state: issue.state,
            labels: issue.labels?.map(l => l.name) || [],
            repository: payload.repository?.full_name
          },
          ache_level: acheLevel
        })
        .select()
        .single()

      if (acheError) {
        console.error('Failed to create ache event for issue:', acheError)
      } else {
        acheEventId = acheEvent.id
        console.log(`Created ache event ${acheEventId} for issue ${issue.number} (ache: ${acheLevel})`)

        // Trigger ScarIndex calculation
        const { data: calculation, error: calcError } = await supabase
          .rpc('coherence_calculation', { event_id: acheEventId })

        if (calcError) {
          console.error('Failed to calculate ScarIndex:', calcError)
        } else {
          console.log(`ScarIndex calculated: ${calculation?.scarindex}`)
        }
      }
    } else {
      console.log(`Unhandled event type: ${eventType}`)
    }

    // Mark webhook as processed
    await supabase
      .from('github_webhooks')
      .update({ 
        processed: true,
        processed_at: new Date().toISOString(),
        ache_event_id: acheEventId
      })
      .eq('id', webhookRecord.id)

    return new Response(
      JSON.stringify({ 
        success: true, 
        event_type: eventType,
        ache_event_id: acheEventId
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    console.error('Webhook processing error:', error)
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: error.message 
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})
