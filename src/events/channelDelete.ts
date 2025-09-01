import { DMChannel, Events, GuildChannel } from 'discord.js';
import axios from 'axios';
import config from '../core/config';

async function handleChannelDelete(channel: DMChannel | GuildChannel) {
    // Ignore DMs
    if (channel instanceof DMChannel) {
        return;
    }

    console.log(`Channel deleted: ${channel.name} (${channel.id})`);

    try {
        const response = await axios.delete(`${config.apiBaseUrl}/channels/${channel.id}`);
        if (response.data.message) {
            console.log(`[CLEANUP] Backend response for channel ${channel.id} deletion: ${response.data.message}`);
        }
    } catch (error) {
        console.error(`[CLEANUP] Failed to notify backend of channel ${channel.id} deletion:`, error);
    }
}

export default {
    name: Events.ChannelDelete,
    execute: handleChannelDelete,
};
