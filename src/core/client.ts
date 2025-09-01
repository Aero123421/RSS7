import { Client, Collection, GatewayIntentBits } from 'discord.js';

// discord.jsのClientを拡張して、コマンドを保持するCollectionを追加
class CustomClient extends Client {
    commands: Collection<string, any> = new Collection();
}

// Botが必要とするIntentsを設定
const client = new CustomClient({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildMembers,
    ],
});

export default client;
