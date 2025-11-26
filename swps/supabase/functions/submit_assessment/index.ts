// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';

interface SubmitPayload {
  assignmentId?: string;
  eventId?: string;
  witnessHandle: string;
  verdict: string;
  notes?: string;
  score?: number;
}

Deno.serve(async (req) => {
  try {
    const body = (await req.json()) as SubmitPayload;
    const { witnessHandle, verdict } = body;
    if (!verdict) throw new Error('verdict is required');

    const { data: witness, error: witnessError } = await supabase
      .from('participants')
      .upsert({ handle: witnessHandle })
      .select('id')
      .single();
    if (witnessError) throw witnessError;

    const eventId = body.eventId;
    if (!eventId) {
      throw new Error('eventId is required');
    }

    const { data: assessment, error } = await supabase
      .from('assessments')
      .insert({
        event_id: eventId,
        witness_id: witness.id,
        verdict,
        notes: body.notes,
        score: body.score ?? 0,
      })
      .select('*')
      .single();

    if (error) throw error;

    const { data: event, error: eventError } = await supabase
      .from('witness_events')
      .select('mode')
      .eq('id', eventId)
      .single();
    if (eventError) throw eventError;

    await supabase
      .from('assignments')
      .update({ status: 'submitted' })
      .eq('event_id', eventId)
      .eq('witness_id', witness.id);

    return new Response(JSON.stringify({ assessment, event }), { status: 200 });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
