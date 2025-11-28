const { SlashCommandBuilder } = require('discord.js');
const { createClient } = require('@supabase/supabase-js');

// Initialize Supabase client directly since this is a simple query
// In a real bot, this would likely use a shared client instance
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

module.exports = {
    data: new SlashCommandBuilder()
        .setName('autopoiesis_guard')
        .setDescription('Show current Autopoiesis Safety Policy (J0_DEFAULT)'),
    async execute(interaction) {
        await interaction.reply('Fetching safety policy...');

        try {
            const { data, error } = await supabase
                .from('structural_safety_policies')
                .select('*')
                .eq('code', 'J0_DEFAULT')
                .single();

            if (error) throw error;

            if (data) {
                const response = `**Autopoiesis Safety Policy (J0_DEFAULT)**
Description: ${data.description}
Min \u03c4-Alignment: ${data.tau_min_alignment}
Max Negative Coherence Delta: ${data.max_negative_coherence_delta}
Max Complexity Score: ${data.max_complexity_score}
Active: ${data.active}`;
                interaction.followUp(response);
            } else {
                interaction.followUp('Policy J0_DEFAULT not found.');
            }
        } catch (error) {
            console.error('Error fetching policy:', error);
            interaction.followUp('Failed to fetch safety policy.');
        }
    },
};
