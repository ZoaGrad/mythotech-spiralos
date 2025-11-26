// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';
import { variantWitnessTargets } from '../_shared/variants.ts';

Deno.serve(async (req) => {
  try {
    const { eventId } = await req.json();
    if (!eventId) throw new Error('eventId is required');

    const { data: event, error: eventError } = await supabase
      .from('witness_events')
      .select('*')
      .eq('id', eventId)
      .single();
    if (eventError) throw eventError;

    const required = variantWitnessTargets[event.mode as keyof typeof variantWitnessTargets];
    const { data: assessments, error: assessError } = await supabase
      .from('assessments')
      .select('score, verdict')
      .eq('event_id', eventId);
    if (assessError) throw assessError;

    if (assessments.length < required) {
      return new Response(JSON.stringify({ message: 'Not enough assessments to finalize' }), { status: 400 });
    }

    const meanScore =
      assessments.reduce((total, item) => total + Number(item.score), 0) / assessments.length;
    const verdicts = assessments.map((a) => a.verdict);
    const verdictTally = verdicts.reduce<Record<string, number>>((acc, v) => {
      acc[v] = (acc[v] ?? 0) + 1;
      return acc;
    }, {});
    const resolvedVerdict = Object.entries(verdictTally).sort((a, b) => b[1] - a[1])[0][0];

    const status = meanScore >= 0 ? 'finalized' : 'escalated';
    const { error: updateError } = await supabase
      .from('witness_events')
      .update({ status })
      .eq('id', eventId);
    if (updateError) throw updateError;

    return new Response(
      JSON.stringify({
        verdict: resolvedVerdict,
        score: meanScore,
        status,
      }),
      { status: 200 },
    );
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
