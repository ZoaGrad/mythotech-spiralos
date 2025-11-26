import express from 'express';
import dotenv from 'dotenv';
import { createClient } from '@supabase/supabase-js';
import { requiredWitnesses } from '../guardian-bot/utils/variantRules.js';

dotenv.config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
if (!supabaseUrl || !supabaseKey) {
  throw new Error('Missing Supabase configuration');
}
const supabase = createClient(supabaseUrl, supabaseKey);

const app = express();
app.use(express.json());

app.post('/claim', async (req, res) => {
  try {
    const { initiatorHandle, targetHandle, mode, payload, resonance = 0, emp_stake = 0 } = req.body;
    const required = requiredWitnesses[mode];
    const { data, error } = await supabase.functions.invoke('create_witness_event', {
      body: { initiatorHandle, targetHandle, mode, payload, resonance, emp_stake },
    });
    if (error) throw error;
    res.json({ event: data.event, required });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.post('/assessment', async (req, res) => {
  try {
    const { witnessHandle, eventId, verdict, notes, score } = req.body;
    const { data, error } = await supabase.functions.invoke('submit_assessment', {
      body: { witnessHandle, eventId, verdict, notes, score },
    });
    if (error) throw error;
    res.json(data);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.post('/resolve', async (req, res) => {
  try {
    const { eventId } = req.body;
    const { data, error } = await supabase.functions.invoke('finalize_claim', { body: { eventId } });
    if (error) throw error;
    res.json(data);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.get('/status/:claimId', async (req, res) => {
  const claimId = req.params.claimId;
  const { data, error } = await supabase.from('witness_events').select('*').eq('id', claimId).single();
  if (error) return res.status(404).json({ error: error.message });
  return res.json(data);
});

app.get('/graph/:participantId', async (req, res) => {
  const participantId = req.params.participantId;
  const { data: events } = await supabase
    .from('witness_events')
    .select('id, mode, initiator, target, created_at')
    .or(`initiator.eq.${participantId},target.eq.${participantId}`);
  const { data: edges } = await supabase
    .from('ancestry_edges')
    .select('*')
    .in('parent_event', events?.map((e) => e.id) ?? []);
  return res.json({ events: events ?? [], edges: edges ?? [] });
});

const port = process.env.PORT || 4000;
app.listen(port, () => {
  console.log(`SWPS API listening on ${port}`);
});
