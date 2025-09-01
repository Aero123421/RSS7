import { Events, Guild } from 'discord.js';
import axios from 'axios';
import config from '../core/config';

async function handleGuildCreate(guild: Guild) {
    console.log(`Joined a new guild: ${guild.name} (${guild.id})`);

    try {
        // Fetch admin IDs from the backend
        const response = await axios.get(`${config.apiBaseUrl}/config`);
        const adminIds = response.data.admin_ids as string[] | undefined;

        if (!adminIds || adminIds.length === 0) {
            console.log('No admin IDs configured to notify.');
            return;
        }

        const message = `新しいサーバー「${guild.name}」に参加しました。`;

        for (const adminId of adminIds) {
            try {
                const adminUser = await guild.client.users.fetch(adminId);
                await adminUser.send(message);
                console.log(`Notified admin ${adminUser.tag}`);
            } catch (error) {
                console.error(`Failed to send DM to admin ${adminId}:`, error);
            }
        }
    } catch (error) {
        console.error('Failed to fetch config or notify admins on guild join:', error);
    }
}

export default {
    name: Events.GuildCreate,
    execute: handleGuildCreate,
};
