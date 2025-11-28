const { SlashCommandBuilder } = require('discord.js');
const { exec } = require('child_process');
const path = require('path');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('autopoiesis_queue')
        .setDescription('List pending structural change requests'),
    async execute(interaction) {
        await interaction.reply('Fetching autopoiesis queue...');

        const scriptPath = path.join(__dirname, '../../../scripts/spiralctl.py');
        const command = `python "${scriptPath}" autopoiesis queue`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                interaction.followUp('Failed to fetch queue.');
                return;
            }

            if (stdout.trim()) {
                interaction.followUp(`**Pending Requests:**\n\`\`\`\n${stdout}\n\`\`\``);
            } else {
                interaction.followUp('No pending requests.');
            }
        });
    },
};
