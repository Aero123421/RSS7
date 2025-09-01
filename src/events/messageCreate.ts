import { Events, Message } from 'discord.js';
import axios from 'axios';
import client from '../core/client';
import config from '../core/config';

async function handleMessageCreate(message: Message) {
    // Ignore bots
    if (message.author.bot) return;

    // Check if it's a reply to our bot
    if (message.reference && message.reference.messageId) {
        try {
            const repliedTo = await message.channel.messages.fetch(message.reference.messageId);

            if (repliedTo.author.id === client.user?.id) {
                // It's a reply to our bot, process as a Q&A
                await message.channel.sendTyping();

                const response = await axios.post(`${config.apiBaseUrl}/qa`, {
                    original_message_id: repliedTo.id,
                    question: message.content,
                });

                const answer = response.data.answer;
                if (answer) {
                    await message.reply(answer);
                } else {
                    await message.reply("申し訳ありませんが、回答を生成できませんでした。");
                }
            }
        } catch (error) {
            console.error('[QA] Error processing Q&A reply:', error);
            await message.reply("エラーが発生し、質問を処理できませんでした。");
        }
    }
}

export default {
    name: Events.MessageCreate,
    execute: handleMessageCreate,
};
