import logging

import discord

from settings import load_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready() -> None:
    logger.info("Logged in as %s", client.user)


def main() -> None:
    """Start the Discord bot."""
    logger.info("Starting RSS7 Discord Bot...")
    settings = load_settings()
    try:
        client.run(settings.DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        logger.error("Invalid DISCORD_TOKEN. Update .env and try again.")
        logger.info("After fixing the token, run: py -m src.bot")


if __name__ == "__main__":
    main()
