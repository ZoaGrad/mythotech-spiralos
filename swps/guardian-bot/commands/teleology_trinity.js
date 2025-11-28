const { SlashCommandBuilder } = require('discord.js');
const { exec } = require('child_process');
const path = require('path');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('teleology_trinity')
        .setDescription('Activate the Teleology Trinity Mandates'),
    async execute(interaction) {
        await interaction.reply('Activating Teleology Trinity...');

        const scriptPath = path.join(__dirname, '../../../scripts/spiralctl.py');
        const command = `python "${scriptPath}" purpose activate-trinity`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                interaction.followUp('Teleology Trinity activation failed—check Guardian logs.');
                return;
            }

            if (stdout.includes('status=broadcasted') || stdout.includes('status=upserted_only')) {
                interaction.followUp('Teleology Trinity \u0394\u03a9.I.1\u20133 is active and broadcast.');
            } else {
                interaction.followUp('Teleology Trinity activation completed with unexpected output.');
            }
        });
    },
};
