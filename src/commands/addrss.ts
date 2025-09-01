import { SlashCommandBuilder, ChatInputCommandInteraction, EmbedBuilder, ChannelType, PermissionsBitField, TextChannel } from 'discord.js';
import axios from 'axios';
import config from '../core/config';
import { getChannelNameForFeed } from '../utils/helpers'; // このヘルパー関数は後で作成

export default {
    data: new SlashCommandBuilder()
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
                .setDescription('既存のチャンネル')
                .addChannelTypes(ChannelType.GuildText))
        .addStringOption(option =>
            option.setName('summary_length')
                .setDescription('要約の長さ')
                .setChoices(
                    { name: '短め', value: 'short' },
                    { name: '通常', value: 'normal' },
                    { name: '長め', value: 'long' }
                )),

    async execute(interaction: ChatInputCommandInteraction) {
        if (!interaction.guild) {
            await interaction.reply({ content: 'このコマンドはサーバー内でのみ使用できます。', ephemeral: true });
            return;
        }

        await interaction.deferReply({ ephemeral: true });

        const url = interaction.options.getString('url', true);
        const summaryLength = interaction.options.getString('summary_length') || 'normal';
        const channelName = interaction.options.getString('channel_name');
        const existingChannel = interaction.options.getChannel('existing_channel');

        try {
            // 1. Add feed to backend (without channel assignment)
            const addFeedResponse = await axios.post(`${config.apiBaseUrl}/feeds`, {
                url: url,
                summary_type: summaryLength,
            });

            const feedInfo = addFeedResponse.data.feed_info;
            const feedTitle = feedInfo.title || 'Unknown Feed';

            let channel: TextChannel | null = null;

            // 2. Determine the channel
            if (existingChannel) {
                channel = existingChannel as TextChannel;
            } else {
                const finalChannelName = channelName || getChannelNameForFeed(url, feedTitle);

                // Check if channel already exists
                let existing = interaction.guild.channels.cache.find(c => c.name === finalChannelName && c.type === ChannelType.GuildText) as TextChannel;

                if (existing) {
                    channel = existing;
                } else {
                    // Create a new channel
                    const { data: apiConfig } = await axios.get(`${config.apiBaseUrl}/config`);
                    const category = apiConfig.category_id ? interaction.guild.channels.cache.get(apiConfig.category_id) : null;

                    channel = await interaction.guild.channels.create({
                        name: finalChannelName,
                        type: ChannelType.GuildText,
                        topic: `RSS Feed: ${feedTitle} | ${url}`,
                        parent: category && category.type === ChannelType.GuildCategory ? category.id : null,
                    });
                }
            }

            if (!channel) {
                throw new Error('チャンネルの取得または作成に失敗しました。');
            }

            // 3. Assign channel to feed in backend
            await axios.post(`${config.apiBaseUrl}/feeds/assign-channel`, null, {
                params: {
                    url: url,
                    channel_id: channel.id,
                    channel_name: channel.name,
                }
            });

            await interaction.editReply(`フィード「${feedTitle}」を追加し、チャンネル ${channel.toString()} に関連付けました。`);

        } catch (error: any) {
            console.error('Error adding RSS feed:', error);
            const errorMessage = error.response?.data?.detail || 'フィードの追加中にエラーが発生しました。';
            await interaction.editReply({ content: errorMessage });
        }
    },
};
