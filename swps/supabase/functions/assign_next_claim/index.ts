// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';
import { variantWitnessTargets } from '../_shared/variants.ts';

interface AssignPayload {
  witnessHandle: string;
}

async function upsertParticipant(handle: string) {
  const { data, error } = await supabase
    .from('participants')
    .upsert({ handle })
    .select('id')
    .single();
  if (error) throw error;
  return data.id as string;
}

Deno.serve(async (req) => {
  try {
    const body = (await req.json()) as AssignPayload;
    const witnessId = await upsertParticipant(body.witnessHandle);

    const { data: claim, error: eventError } = await supabase
      .from('witness_events')
      .select('*')
      .eq('status', 'pending')
      .order('resonance', { ascending: false })
      .order('created_at', { ascending: true })
      .limit(1)
      .single();

    if (eventError) throw eventError;
    const required = variantWitnessTargets[claim.mode as keyof typeof variantWitnessTargets];

    const { data: existingAssignments, error: assignmentFetchError } = await supabase
      .from('assignments')
      .select('id')
      .eq('event_id', claim.id);

    if (assignmentFetchError) throw assignmentFetchError;
    if (existingAssignments.length >= required) {
      return new Response(JSON.stringify({ message: 'All witnesses already assigned' }), { status: 400 });
    }

    const { data: assignment, error } = await supabase
      .from('assignments')
      .insert({ event_id: claim.id, witness_id: witnessId })
      .select('*')
      .single();

    if (error) throw error;

    await supabase.from('witness_events').update({ status: 'assigned' }).eq('id', claim.id);

    return new Response(JSON.stringify({ assignment, claim }), { status: 200 });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
