import { SlashCommandBuilder } from 'discord.js';
import { supabase } from '../utils/supabaseClient.js';

export const data = new SlashCommandBuilder()
  .setName('status')
  .setDescription('Check claim status')
  .addStringOption((opt) => opt.setName('event_id').setDescription('Event id').setRequired(true));

export async function execute(interaction) {
  const eventId = interaction.options.getString('event_id');
  const { data, error } = await supabase.from('witness_events').select('*').eq('id', eventId).single();
  if (error) return interaction.reply({ content: `Error: ${error.message}`, ephemeral: true });
  return interaction.reply({
    content: `Event ${eventId}: status=${data.status}, mode=${data.mode}, required=${data.required_witnesses}`,
    ephemeral: true,
  });
}
