// deno-lint-ignore-file no-explicit-any
import { supabase } from '../_shared/client.ts';

interface EdgePayload {
  parentEvent: string;
  childEvent: string;
  weight?: number;
  permanence?: boolean;
  decay_rate?: number;
}

Deno.serve(async (req) => {
  try {
    const body = (await req.json()) as EdgePayload;
    if (!body.parentEvent || !body.childEvent) {
      throw new Error('parentEvent and childEvent are required');
    }

    const { data, error } = await supabase
      .from('ancestry_edges')
      .insert({
        parent_event: body.parentEvent,
        child_event: body.childEvent,
        weight: body.weight ?? 1,
        permanence: body.permanence ?? false,
        decay_rate: body.decay_rate,
      })
      .select('*')
      .single();
    if (error) throw error;

    return new Response(JSON.stringify({ edge: data }), { status: 200 });
  } catch (error: any) {
    return new Response(JSON.stringify({ error: error.message }), { status: 400 });
  }
});
