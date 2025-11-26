import { Client, Collection, GatewayIntentBits } from 'discord.js';
import dotenv from 'dotenv';
import * as claim from './commands/claim.js';
import * as witness from './commands/witness.js';
import * as status from './commands/status.js';

dotenv.config();

const client = new Client({ intents: [GatewayIntentBits.Guilds] });
const commands = new Collection();
[claim, witness, status].forEach((cmd) => commands.set(cmd.data.name, cmd));

client.once('ready', () => {
  console.log(`Guardian bot ready as ${client.user.tag}`);
});

client.on('interactionCreate', async (interaction) => {
  if (!interaction.isChatInputCommand()) return;
  const command = commands.get(interaction.commandName);
  if (!command) return;
  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.editReply({ content: 'There was an error while executing this command!' });
    } else {
      await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
    }
  }
});

client.login(process.env.DISCORD_TOKEN);
