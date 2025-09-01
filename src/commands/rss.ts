import { SlashCommandBuilder, ChatInputCommandInteraction, EmbedBuilder } from 'discord.js';
import axios from 'axios';
import config from '../core/config';

import { SlashCommandBuilder, ChatInputCommandInteraction, EmbedBuilder } from 'discord.js';
import axios from 'axios';
import config from '../core/config';

export default {
    data: new SlashCommandBuilder()
        .setName('rss')
        .setDescription('RSSフィード関連のコマンド')
        .addSubcommand(subcommand =>
            subcommand
                .setName('status')
                .setDescription('ボットのステータスを表示します'))
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
                .setDescription('登録されているフィードの一覧を表示します')),

    async execute(interaction: ChatInputCommandInteraction) {
        const subcommand = interaction.options.getSubcommand();

        if (subcommand === 'status') {
            try {
                await interaction.deferReply({ ephemeral: true });

                // APIから設定とフィード情報を取得
                const { data: apiConfig } = await axios.get(`${config.apiBaseUrl}/config`);
                const { data: feeds } = await axios.get(`${config.apiBaseUrl}/feeds`);

                const embed = new EmbedBuilder()
                    .setTitle('RSS Bot ステータス')
                    .setColor(apiConfig.embed_color || 0x3498db)
                    .addFields(
                        { name: '登録フィード数', value: String(feeds.length), inline: true },
                        { name: '確認間隔', value: `${apiConfig.check_interval || 15}分`, inline: true },
                        { name: 'AIモデル', value: apiConfig.ai_model || 'N/A', inline: true },
                        { name: '要約', value: apiConfig.summarize ? '有効' : '無効', inline: true }
                    )
                    .setFooter({ text: `最終更新: ${new Date().toLocaleString('ja-JP')}` });

                await interaction.editReply({ embeds: [embed] });

            } catch (error) {
                console.error('Error fetching bot status:', error);
                await interaction.editReply({ content: 'ステータスの取得中にエラーが発生しました。' });
            }
        } else if (subcommand === 'list_feeds') {
            try {
                await interaction.deferReply({ ephemeral: true });
                const { data: feeds } = await axios.get(`${config.apiBaseUrl}/feeds`);

                if (!feeds || feeds.length === 0) {
                    await interaction.editReply('登録されているRSSフィードはありません。');
                    return;
                }

                const embed = new EmbedBuilder()
                    .setTitle('登録済みRSSフィード一覧')
                    .setColor(0x3498db);

                let description = '';
                for (const feed of feeds) {
                    const channel = feed.channel_id ? `<#${feed.channel_id}>` : '未割り当て';
                    description += `**${feed.title}**\n- URL: ${feed.url}\n- 投稿先: ${channel}\n\n`;
                }
                embed.setDescription(description.substring(0, 4090));

                await interaction.editReply({ embeds: [embed] });

            } catch (error) {
                console.error('Error fetching feed list:', error);
                await interaction.editReply({ content: 'フィード一覧の取得中にエラーが発生しました。' });
            }

        } else if (subcommand === 'check_now') {
            if (!interaction.channelId) {
                await interaction.reply({ content: 'このコマンドはチャンネル内でのみ使用できます。', ephemeral: true });
                return;
            }
            try {
                await interaction.deferReply();
                const { data } = await axios.post(`${config.apiBaseUrl}/feeds/check-now`, {
                    channel_id: interaction.channelId,
                });

                if (data.article_data) {
                    const { postArticle } = await import('../core/postArticle');
                    await postArticle(interaction.client, data.article_data.processed_article, data.article_data.channel_id);
                    await interaction.editReply('最新の記事を取得し、投稿しました。');
                } else {
                    await interaction.editReply(data.message || '新しい記事は見つかりませんでした。');
                }
            } catch (error: any) {
                const errorMessage = error.response?.data?.detail || '記事の取得中にエラーが発生しました。';
                console.error('Error checking feed now:', error);
                await interaction.editReply({ content: errorMessage });
            }
        } else if (subcommand === 'config') {
            // TODO: Implement a proper UI like the python version
            await interaction.reply({ content: '設定パネルは現在開発中です。', ephemeral: true });
        }
    },
};
