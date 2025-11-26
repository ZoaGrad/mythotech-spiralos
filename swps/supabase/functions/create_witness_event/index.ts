// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';
import { variantWitnessTargets, validateStake } from '../_shared/variants.ts';
import type { WitnessMode } from '../../../shared/types.ts';

interface CreateWitnessPayload {
  initiatorHandle: string;
  targetHandle?: string;
  mode: WitnessMode;
  payload: Record<string, unknown>;
  emp_stake?: number;
  resonance?: number;
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
    const body = (await req.json()) as CreateWitnessPayload;
    const mode = body.mode;
    validateStake(mode, body.emp_stake ?? 0);

    const initiator = await upsertParticipant(body.initiatorHandle);
    const target = body.targetHandle ? await upsertParticipant(body.targetHandle) : null;

    const required_witnesses = variantWitnessTargets[mode];
    const { data, error } = await supabase
      .from('witness_events')
      .insert({
        initiator,
        target,
        mode,
        payload: body.payload,
        emp_stake: body.emp_stake ?? 0,
        resonance: body.resonance ?? 0,
        required_witnesses,
      })
      .select('*')
      .single();

    if (error) throw error;
    return new Response(JSON.stringify({ event: data }), { status: 200 });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
