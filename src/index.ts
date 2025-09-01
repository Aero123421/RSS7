import fs from 'node:fs';
import path from 'node:path';
import { Events } from 'discord.js';
import client from './core/client';
import config from './core/config';
import handleInteraction from './events/interactionCreate';

// --- Main Function ---
async function main() {
    // --- Command Loader ---
    const commandsPath = path.join(__dirname, 'commands');
    const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.ts') || file.endsWith('.js'));

    for (const file of commandFiles) {
        const filePath = path.join(commandsPath, file);
        try {
            const command = (await import(filePath)).default;
            if ('data' in command && 'execute' in command) {
                client.commands.set(command.data.name, command);
                console.log(`[SUCCESS] Loaded command ${command.data.name}`);
            } else {
                console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
            }
        } catch (error) {
            console.error(`[ERROR] Failed to load command at ${filePath}:`, error);
        }
    }

    // --- Event Handlers ---
    client.once(Events.ClientReady, c => {
        console.log(`Ready! Logged in as ${c.user.tag}`);
        console.log(`API URL: ${config.apiBaseUrl}`);
    });

    client.on(Events.InteractionCreate, handleInteraction);

    // BotをDiscordにログインさせる
    await client.login(config.discordToken);
}

console.log('Bot is starting...');
main().catch(console.error);
