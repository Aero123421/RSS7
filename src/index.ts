import fs from 'node:fs';
import path from 'node:path';
import { ActivityType, Events } from 'discord.js';
import axios from 'axios';
import client from './core/client';
import config from './core/config';
import handleInteraction from './events/interactionCreate';
import { postArticle } from './core/postArticle'; // We will create this file

// --- Polling function for new articles ---
async function pollAndPostArticles() {
    try {
        const response = await axios.get(`${config.apiBaseUrl}/articles-to-post`);
        const articleData = response.data;

        if (articleData && articleData.processed_article && articleData.channel_id) {
            console.log(`[POLL] Found new article to post: ${articleData.processed_article.title}`);
            await postArticle(client, articleData.processed_article, articleData.channel_id);
        }
    } catch (error) {
        // Don't log error if it's just an empty response (which is normal)
        if (axios.isAxiosError(error) && error.response?.status !== 404) {
            console.error('[POLL] Error fetching articles to post:', error.message);
        }
    }
}

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

        // Set presence
        client.user?.setActivity('RSS Feeds', { type: ActivityType.Watching });

        // Start polling for articles
        setInterval(pollAndPostArticles, 20 * 1000); // Poll every 20 seconds
        console.log('Started polling for new articles.');
    });

    // --- Event Loader ---
    const eventsPath = path.join(__dirname, 'events');
    const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.ts') || file.endsWith('.js'));

    for (const file of eventFiles) {
        const filePath = path.join(eventsPath, file);
        try {
            const event = (await import(filePath)).default;
            if (event.once) {
                client.once(event.name, (...args) => event.execute(...args));
            } else {
                client.on(event.name, (...args) => event.execute(...args));
            }
            console.log(`[SUCCESS] Loaded event ${event.name}`);
        } catch (error) {
            console.error(`[ERROR] Failed to load event at ${filePath}:`, error);
        }
    }

    // BotをDiscordにログインさせる
    await client.login(config.discordToken);
}

console.log('Bot is starting...');
main().catch(console.error);
