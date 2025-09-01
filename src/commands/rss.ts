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
        }
        // 他のサブコマンドのハンドリングは後で追加
    },
};
