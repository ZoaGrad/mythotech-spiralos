const { SlashCommandBuilder } = require('discord.js');
const { exec } = require('child_process');
const path = require('path');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('autopoiesis_path')
        .setDescription('Manage Autopoiesis Path (Sequence J-D)')
        .addSubcommand(subcommand =>
            subcommand
                .setName('status')
                .setDescription('Show Autopoiesis Status'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('activate')
                .setDescription('Activate Autopoiesis Path')
                .addStringOption(option =>
                    option.setName('path')
                        .setDescription('Path ID')
                        .setRequired(true)
                        .addChoices({ name: 'JD', value: 'JD' })))
        .addSubcommand(subcommand =>
            subcommand
                .setName('phase')
                .setDescription('Set Autopoiesis Phase')
                .addStringOption(option =>
                    option.setName('phase')
                        .setDescription('Phase ID')
                        .setRequired(true)
                        .addChoices(
                            { name: 'J1', value: 'j1' },
                            { name: 'J2', value: 'j2' },
                            { name: 'J3', value: 'j3' }
                        )))
        .addSubcommand(subcommand =>
            subcommand
                .setName('test_membrane')
                .setDescription('Test Autopoiesis Membrane')),
    async execute(interaction) {
        const subcommand = interaction.options.getSubcommand();
        await interaction.reply(`Executing autopoiesis ${subcommand}...`);

        const scriptPath = path.join(__dirname, '../../../scripts/spiralctl.py');
        let args = '';

        if (subcommand === 'status') {
            args = 'autopoiesis status';
        } else if (subcommand === 'activate') {
            const pathId = interaction.options.getString('path');
            args = `autopoiesis activate-path ${pathId}`;
        } else if (subcommand === 'phase') {
            const phaseId = interaction.options.getString('phase');
            args = `autopoiesis phase ${phaseId}`;
        } else if (subcommand === 'test_membrane') {
            args = 'autopoiesis test-membrane --stress --cycles 5';
        }

        const command = `python "${scriptPath}" ${args}`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                interaction.followUp(`Failed to execute ${subcommand}.`);
                return;
            }

            if (stdout.trim()) {
                interaction.followUp(`\`\`\`\n${stdout}\n\`\`\``);
            } else {
                interaction.followUp('Command executed with no output.');
            }
        });
    },
};
