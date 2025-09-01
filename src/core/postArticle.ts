import { Client, EmbedBuilder, TextChannel } from 'discord.js';
import axios from 'axios';
import config from './config';

// Type definition for a processed article from the backend
interface ProcessedArticle {
    title: string;
    link: string;
    summary?: string;
    content?: string;
    published?: string;
    image?: string;
    feed_title?: string;
    category?: string;
    classified?: boolean;
    category_info?: {
        name: string;
        jp_name: string;
        emoji: string;
    };
    keywords_en?: string;
    _original_article: any; // Keep the original article data
}

const categoryColors: { [key: string]: number } = {
    "technology": 0x3498db,
    "business": 0xf1c40f,
    "politics": 0xe74c3c,
    "entertainment": 0x9b59b6,
    "sports": 0x2ecc71,
    "science": 0x1abc9c,
    "health": 0xe67e22,
    "other": 0x95a5a6,
};

function truncate(text: string, maxLength: number): string {
    if (!text) return '';
    // Basic HTML tag removal
    const plainText = text.replace(/<[^>]+>/g, '');
    if (plainText.length <= maxLength) return plainText;
    return plainText.substring(0, maxLength - 3) + '...';
}

export async function postArticle(client: Client, article: ProcessedArticle, channelId: string): Promise<void> {
    try {
        const channel = await client.channels.fetch(channelId);
        if (!channel || !(channel instanceof TextChannel)) {
            console.error(`[POST] Channel ${channelId} not found or not a text channel.`);
            return;
        }

        const category = article.category || 'other';
        const categoryInfo = article.category_info || { name: 'other', jp_name: 'その他', emoji: '📌' };
        const color = categoryColors[category] || categoryColors['other'];

        const embed = new EmbedBuilder()
            .setColor(color)
            .setTitle(`${categoryInfo.emoji} ${article.title}`)
            .setURL(article.link)
            .setDescription(article.summary || truncate(article.content || '', 4000))
            .setFooter({ text: article.feed_title || 'RSS Feed' });

        if (article.classified) {
            embed.addFields({ name: 'カテゴリ', value: `${categoryInfo.emoji} ${categoryInfo.jp_name}`, inline: true });
        }

        if (article.published) {
            try {
                const date = new Date(article.published);
                embed.addFields({ name: '公開日時', value: date.toLocaleString('ja-JP'), inline: true });
            } catch {
                // If date is not valid, just show the string
                embed.addFields({ name: '公開日時', value: article.published, inline: true });
            }
        }

        if (article.image) {
            embed.setThumbnail(article.image);
        }

        const message = await channel.send({ embeds: [embed] });
        console.log(`[POST] Successfully posted article "${article.title}" to #${channel.name}`);

        // Associate the article with the message ID in the backend
        await axios.post(`${config.apiBaseUrl}/articles/associate`, {
            message_id: message.id,
            channel_id: channel.id,
            original_article: article._original_article,
            keywords_en: article.keywords_en || '',
        });
        console.log(`[POST] Associated message ${message.id} with article.`);

    } catch (error) {
        console.error(`[POST] Failed to post article "${article.title}" to channel ${channelId}:`, error);
    }
}
