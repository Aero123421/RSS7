import { Interaction, Events } from 'discord.js';

async function handleInteraction(interaction: Interaction) {
    if (!interaction.isChatInputCommand()) return;

    // Get command from the client's command collection
    const command = interaction.client.commands.get(interaction.commandName);

    if (!command) {
        console.error(`No command matching ${interaction.commandName} was found.`);
        await interaction.reply({ content: `コマンド「${interaction.commandName}」が見つかりません。`, ephemeral: true });
        return;
    }

    try {
        await command.execute(interaction);
    } catch (error) {
        console.error(`Error executing ${interaction.commandName}`, error);
        const errorMessage = 'コマンド実行中にエラーが発生しました。';
        if (interaction.replied || interaction.deferred) {
            await interaction.followUp({ content: errorMessage, ephemeral: true });
        } else {
            await interaction.reply({ content: errorMessage, ephemeral: true });
        }
    }
}

export default {
    name: Events.InteractionCreate,
    execute: handleInteraction,
};
