// SpiralOS GitHub Webhook Edge Function
// Ingests GitHub events and converts them to Ache measurements
// ΔΩ.126.0 - Constitutional Cognitive Sovereignty

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

// Configuration constants - adjust these for production tuning
const MAX_FILES_CHANGED_THRESHOLD = parseInt(Deno.env.get('ACHE_MAX_FILES') || '20')
const MIN_COMMIT_MESSAGE_LENGTH = parseInt(Deno.env.get('ACHE_MIN_MESSAGE_LENGTH') || '50')

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
  ref?: string
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
  // Normalize to [0, 1] range using configured threshold
  const changeAche = Math.min(totalChanges / MAX_FILES_CHANGED_THRESHOLD, 0.8)
  
  // Message quality affects ache (poor messages = higher ache)
  const messageLength = commit.message?.length || 0
  const messageQuality = messageLength > MIN_COMMIT_MESSAGE_LENGTH ? 0.1 : 0.3
  
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
    const startedAt = performance.now()
    let supabaseCallCount = 0
    const trackSupabaseCall = async <T>(promise: Promise<T>): Promise<T> => {
      supabaseCallCount += 1
      return promise
    }
    const logTelemetry = (status: string) => {
      const durationMs = performance.now() - startedAt
      console.log(
        `[telemetry] status=${status} duration=${durationMs.toFixed(2)}ms supabase_calls=${supabaseCallCount}`
      )
    }

    // Parse webhook
    const eventType = req.headers.get('x-github-event')
    const payload: WebhookPayload = await req.json()

    console.log(`Received GitHub webhook: ${eventType}`)
    
    // Early guard: Ignore non-push and non-issues events
    if (eventType !== 'push' && eventType !== 'issues') {
      console.log(`Ignoring unsupported event type: ${eventType}`)
      logTelemetry('ignored')
      return new Response(
        JSON.stringify({
          success: true,
          message: `Event type '${eventType}' not processed`,
          event_type: eventType
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200
        }
      )
    }
    
    // Early guard: For issues events, only process 'opened' action
    if (eventType === 'issues' && payload.action !== 'opened') {
      console.log(`Ignoring issues event with action: ${payload.action}`)
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: `Issues action '${payload.action}' not processed`,
          event_type: eventType
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200
        }
      )
    }
    
    // Early guard: For push events, ensure we have commits
    if (eventType === 'push' && (!payload.commits || payload.commits.length === 0)) {
      console.log('Ignoring push event with no commits')
      return new Response(
        JSON.stringify({ 
          success: true, 
          message: 'Push event with no commits not processed',
          event_type: eventType
        }),
        { 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 200
        }
      )
    }

    let acheEventId: string | null = null

    // Process based on event type
    if (eventType === 'push' && payload.commits && payload.commits.length > 0) {
      const commitsWithAche = payload.commits.map(commit => ({
        ...commit,
        ache_level: computeAcheFromCommit(commit)
      }))

      const { data: batchResult, error: batchError } = await trackSupabaseCall(
        supabase.rpc('process_push_batch', {
          commits: commitsWithAche,
          repository: payload.repository?.full_name ?? null,
          branch_ref: payload.ref ?? null
        })
      )

      if (batchError) {
        console.error('process_push_batch error:', batchError)
        throw batchError
      }

      acheEventId = batchResult?.ache_event_ids?.[0] ?? null
      console.log(
        `Processed push with ${batchResult?.processed_count || 0} commits (avg ache ${batchResult?.average_ache ?? 0})`
      )
    } else if (eventType === 'issues' && payload.action === 'opened' && payload.issue) {
      // Process new issue
      const issue = payload.issue
      const acheLevel = nlpAcheScore(issue.body)
      const issueExternalId = `issue_${issue.number}`
      
      // Check if this issue was already processed
      const { data: existingIndex } = await trackSupabaseCall(
        supabase
          .from('scar_index')
          .select('id, processing_status, scarindex_value')
          .eq('external_id', issueExternalId)
          .eq('external_source', 'github_issue')
          .single()
      )
      
      if (existingIndex && existingIndex.processing_status === 'completed') {
        console.log(`Issue ${issue.number} already processed (ScarIndex: ${existingIndex.scarindex_value})`)
        // Skip this issue as it was already processed
      } else {
        // Create or update scar_index entry
        const { data: scarIndexEntry } = await trackSupabaseCall(
          supabase
          .from('scar_index')
          .upsert({
            external_id: issueExternalId,
            external_source: 'github_issue',
            processing_status: 'processing',
            metadata: { issue_title: issue.title }
          }, {
            onConflict: 'external_id'
          })
          .select()
          .single()
        )
        
        // Create Ache event using upsert
        const { data: acheEvent, error: acheError } = await trackSupabaseCall(
          supabase
          .from('ache_events')
          .upsert({
            source: 'github_issue',
            source_id: issueExternalId,
            content: {
              number: issue.number,
              title: issue.title,
              body: issue.body,
              state: issue.state,
              labels: issue.labels?.map(l => l.name) || [],
              repository: payload.repository?.full_name
            } || {},
            ache_level: acheLevel,
            metadata: {}
          }, {
            onConflict: 'source_id'
          })
          .select()
          .single()
        )

        if (acheError) {
          console.error('Failed to create ache event for issue:', acheError)
          
          // Update scar_index with error
          await trackSupabaseCall(
            supabase
            .from('scar_index')
            .update({
              processing_status: 'failed',
              error_message: acheError.message,
              retry_count: (scarIndexEntry?.retry_count || 0) + 1
            })
            .eq('external_id', issueExternalId)
          )
        } else {
          acheEventId = acheEvent.id
          console.log(`Created ache event ${acheEventId} for issue ${issue.number} (ache: ${acheLevel})`)

          // Trigger ScarIndex calculation
          const { data: calculation, error: calcError } = await trackSupabaseCall(
            supabase
            .rpc('coherence_calculation', { event_id: acheEventId })
          )

          if (calcError) {
            console.error('Failed to calculate ScarIndex:', calcError)

            // Update scar_index with error
            await trackSupabaseCall(
              supabase
              .from('scar_index')
              .update({
                processing_status: 'failed',
                error_message: calcError.message
              })
              .eq('external_id', issueExternalId)
            )
          } else {
            console.log(`ScarIndex calculated: ${calculation?.scarindex}`)

            // Update scar_index with success
            await trackSupabaseCall(
              supabase
              .from('scar_index')
              .update({
                processing_status: 'completed',
                scarindex_value: calculation?.scarindex,
                scarindex_calculation_id: calculation?.id
              })
              .eq('external_id', issueExternalId)
            )
          }
        }
      }
    } else {
      console.log(`Unhandled event type: ${eventType}`)
    }

    logTelemetry('ok')
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
    logTelemetry('error')
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
