import { SlashCommandBuilder } from 'discord.js';
import { invokeFunction } from '../utils/supabaseClient.js';
import { escalationTarget } from '../utils/variantRules.js';

export const data = new SlashCommandBuilder()
  .setName('claim')
  .setDescription('Submit a new witness claim')
  .addStringOption((opt) => opt.setName('mode').setDescription('stream|crucible|council').setRequired(true))
  .addStringOption((opt) => opt.setName('target').setDescription('Target handle').setRequired(false))
  .addStringOption((opt) => opt.setName('payload').setDescription('JSON payload').setRequired(true))
  .addNumberOption((opt) => opt.setName('resonance').setDescription('Resonance score').setRequired(false))
  .addNumberOption((opt) => opt.setName('emp_stake').setDescription('EMP stake for crucible').setRequired(false));

export async function execute(interaction) {
  const mode = interaction.options.getString('mode');
  const payload = interaction.options.getString('payload');
  let parsed;
  try {
    parsed = JSON.parse(payload);
  } catch (err) {
    return interaction.reply({ content: 'Payload must be valid JSON', ephemeral: true });
  }
  const resonance = interaction.options.getNumber('resonance') ?? 0;
  const escalatedMode = escalationTarget(mode, resonance);
  try {
    const result = await invokeFunction('create_witness_event', {
      initiatorHandle: interaction.user.username,
      targetHandle: interaction.options.getString('target') ?? undefined,
      payload: parsed,
      resonance,
      emp_stake: interaction.options.getNumber('emp_stake') ?? undefined,
      mode: escalatedMode,
    });
    return interaction.reply({ content: `Claim created (${escalatedMode}) with id ${result.event.id}` });
  } catch (error) {
    return interaction.reply({ content: `Error: ${error.message}`, ephemeral: true });
  }
}
