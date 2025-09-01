import dotenv from 'dotenv';
import path from 'path';

// .envファイルから環境変数をロード
// プロジェクトルートにある.envファイルを指定
dotenv.config({ path: path.resolve(__dirname, '..', '..', '.env') });

interface Config {
    discordToken: string;
    guildId: string;
    clientId: string;
    apiBaseUrl: string;
}

const config: Config = {
    discordToken: process.env.DISCORD_TOKEN || '',
    guildId: process.env.GUILD_ID || '',
    clientId: process.env.CLIENT_ID || '',
    apiBaseUrl: process.env.API_BASE_URL || 'http://127.0.0.1:8000/api',
};

// 必須の環境変数が設定されているかチェック
if (!config.discordToken || !config.guildId || !config.clientId) {
    throw new Error('DISCORD_TOKEN, GUILD_ID, and CLIENT_ID must be set in the environment variables.');
}

export default config;
