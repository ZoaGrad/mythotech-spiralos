import { SlashCommandBuilder } from 'discord.js';
import { invokeFunction } from '../utils/supabaseClient.js';
import { computeScore, reputationDelta } from '../utils/scoring.js';

export const data = new SlashCommandBuilder()
  .setName('witness')
  .setDescription('Witness workflow')
  .addSubcommand((sub) =>
    sub
      .setName('next')
      .setDescription('Get next claim to witness'),
  )
  .addSubcommand((sub) =>
    sub
      .setName('submit')
      .setDescription('Submit an assessment')
      .addStringOption((opt) => opt.setName('event_id').setDescription('Event id').setRequired(true))
      .addStringOption((opt) => opt.setName('verdict').setDescription('affirm|challenge|abstain').setRequired(true))
      .addStringOption((opt) => opt.setName('notes').setDescription('Notes').setRequired(false))
      .addNumberOption((opt) => opt.setName('score').setDescription('Score delta').setRequired(false)),
  );

export async function execute(interaction) {
  if (interaction.options.getSubcommand() === 'next') {
    try {
      const result = await invokeFunction('assign_next_claim', {
        witnessHandle: interaction.user.username,
      });
      if (result.message) {
        return interaction.reply({ content: result.message, ephemeral: true });
      }
      return interaction.reply({
        content: `Assigned to event ${result.claim.id} (mode: ${result.claim.mode})`,
        ephemeral: true,
      });
    } catch (error) {
      return interaction.reply({ content: `Error: ${error.message}`, ephemeral: true });
    }
  }

  const verdict = interaction.options.getString('verdict');
  const eventId = interaction.options.getString('event_id');
  const notes = interaction.options.getString('notes') ?? '';
  const score = interaction.options.getNumber('score') ?? computeScore(verdict, notes);
  try {
    const assessment = await invokeFunction('submit_assessment', {
      witnessHandle: interaction.user.username,
      eventId,
      verdict,
      notes,
      score,
    });
    await invokeFunction('update_reputation', {
      participantHandle: interaction.user.username,
      delta: reputationDelta(assessment.event.mode ?? 'stream', score),
    });
    return interaction.reply({ content: `Assessment submitted for ${eventId} with score ${score}` });
  } catch (error) {
    return interaction.reply({ content: `Error: ${error.message}`, ephemeral: true });
  }
}
