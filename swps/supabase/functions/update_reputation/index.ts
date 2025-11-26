// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';

interface ReputationPayload {
  participantHandle: string;
  delta: {
    velocity?: number;
    density?: number;
    gravity?: number;
  };
}

Deno.serve(async (req) => {
  try {
    const body = (await req.json()) as ReputationPayload;
    const { participantHandle, delta } = body;
    const { data: participant, error: participantError } = await supabase
      .from('participants')
      .upsert({ handle: participantHandle })
      .select('id')
      .single();
    if (participantError) throw participantError;

    const { data: existing } = await supabase
      .from('participant_reputation')
      .select('*')
      .eq('participant_id', participant.id)
      .single();

    const next = {
      velocity: (existing?.velocity ?? 0) + (delta.velocity ?? 0),
      density: (existing?.density ?? 0) + (delta.density ?? 0),
      gravity: (existing?.gravity ?? 0) + (delta.gravity ?? 0),
      participant_id: participant.id,
    };

    const { data, error } = await supabase
      .from('participant_reputation')
      .upsert(next)
      .select('*')
      .single();
    if (error) throw error;

    return new Response(JSON.stringify({ reputation: data }), { status: 200 });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
