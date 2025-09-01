import { REST, Routes, SlashCommandBuilder } from 'discord.js';
import config from './core/config';

const commands = [
    // /addrss command
    new SlashCommandBuilder()
        .setName('addrss')
        .setDescription('RSSフィードを追加します')
        .addStringOption(option =>
            option.setName('url')
                .setDescription('RSSフィードのURL')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('channel_name')
                .setDescription('チャンネル名（省略可）'))
        .addChannelOption(option =>
            option.setName('existing_channel')
                .setDescription('既存のチャンネル'))
        .addStringOption(option =>
            option.setName('summary_length')
                .setDescription('要約の長さ')
                .setChoices(
                    { name: '短め', value: 'short' },
                    { name: '通常', value: 'normal' },
                    { name: '長め', value: 'long' }
                )),

    // /rss command group
    new SlashCommandBuilder()
        .setName('rss')
        .setDescription('RSSフィード関連のコマンド')
        .addSubcommand(subcommand =>
            subcommand
                .setName('config')
                .setDescription('設定パネルを表示します'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('check_now')
                .setDescription('このチャンネルの最新記事を取得します'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('list_feeds')
                .setDescription('登録されているフィードの一覧を表示します'))
        .addSubcommand(subcommand =>
            subcommand
                .setName('status')
                .setDescription('ボットのステータスを表示します')),
]
.map(command => command.toJSON());

const rest = new REST({ version: '10' }).setToken(config.discordToken);

const rest = new REST({ version: '10' }).setToken(config.discordToken);

console.log('Deploying slash commands...');

rest.put(Routes.applicationGuildCommands(config.clientId, config.guildId), {
    body: commands,
})
    .then(() => console.log('Successfully registered application commands.'))
    .catch(console.error);
