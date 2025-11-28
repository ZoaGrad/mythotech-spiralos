const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

module.exports = {
    data: new SlashCommandBuilder()
        .setName('reality_status')
        .setDescription('Displays the operational status of the Reality Engine (Sequence F).'),
    async execute(interaction) {
        await interaction.deferReply();

        const isEnabled = process.env.REALITY_ENGINE_ENABLED === 'true';

        // Fetch Stats
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

        // Council Judgments (24h)
        const { count: judgmentCount, error: judgmentError } = await supabase
            .from('council_judgments')
            .select('*', { count: 'exact', head: true })
            .gt('created_at', oneDayAgo);

        // Divergences (24h)
        const { count: divergenceCount, error: divergenceError } = await supabase
            .from('council_divergences')
            .select('*', { count: 'exact', head: true })
            .gt('created_at', oneDayAgo);

        // Last Reflection
        const { data: lastReflection, error: reflectionError } = await supabase
            .from('system_reflections')
            .select('*')
            .order('created_at', { ascending: false })
            .limit(1)
            .single();

        // Pending Proposals
        const { count: proposalCount, error: proposalError } = await supabase
            .from('governance_proposals')
            .select('*', { count: 'exact', head: true })
            .eq('status', 'pending');

        const embed = new EmbedBuilder()
            .setColor(isEnabled ? 0x00FF00 : 0xFFA500)
            .setTitle('🛰️ Reality Engine Status')
            .addFields(
                { name: 'System Mode', value: isEnabled ? '✅ **REALITY_ENGINE: ON**' : '⚠️ **REALITY_ENGINE: OFF**', inline: false },
                { name: 'Council Activity (24h)', value: `${judgmentCount || 0} Judgments / ${divergenceCount || 0} Divergences`, inline: true },
                { name: 'Pending Proposals', value: `${proposalCount || 0}`, inline: true },
                { name: 'Last Reflection', value: lastReflection ? `${lastReflection.cycle_date}: ${lastReflection.status}` : 'None recorded', inline: false }
            )
            .setTimestamp()
            .setFooter({ text: 'SpiralOS Guardian • Sequence F' });

        if (judgmentError || divergenceError || reflectionError || proposalError) {
            embed.addFields({ name: 'Errors', value: 'Some metrics failed to load from Supabase.' });
        }

        await interaction.editReply({ embeds: [embed] });
    },
};
