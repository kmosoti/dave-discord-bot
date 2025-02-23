import pathlib
import json
import logging
import discord
import wavelink
import typing
import asyncio
from discord.ext import commands
from utils import config, discord_logger, lavalink_manager 



async def load_extensions():
    cogs_dir = pathlib.Path("cogs")
    for path in cogs_dir.rglob("*.py"):
        if path.stem != "__init__":
            cog_path = ".".join(path.with_suffix("").parts)
            try:
                bot.load_extension(cog_path)  # Ensure we await async setup
                logging.info(f"Loaded cog: {cog_path}")
            except Exception as e:
                logging.error(f"Failed to load cog {cog_path}: {e}")

def load_config(file_path: str) -> dict:
    import json
    with open(file_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    print("Loaded config:", config_data)  # Debug: inspect the config
    if "DISCORD" not in config_data or "DISCORD_TOKEN" not in config_data["DISCORD"]:
        raise Exception("DISCORD_TOKEN not set in configuration file.")
    return config_data

# Set up logging
discord_logger.setup_logging("logs/bot.log")

# Load configuration
config_data = load_config("data/config.json")
TOKEN = config_data["DISCORD"]["DISCORD_TOKEN"]
GUILD_IDS = config_data["DISCORD"].get("GUILD_IDS", [])

# Define the bot's intents
intents = discord.Intents.default()
intents.message_content = True

# Instantiate the bot with our intents and debug_guilds for instant command registration
bot = discord.Bot(intents=intents, debug_guilds=GUILD_IDS)

# Optionally attach config to the bot for easy access in your cogs
bot.config = config_data

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is connected to Discord!")
    if GUILD_IDS:
        logging.info(f"Debugging guilds: {GUILD_IDS}")
    else:
        logging.info("Debugging guilds not set")

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.application_command:
        command_name = interaction.data.get('name')
        user = interaction.user
        channel = interaction.channel
        guild = interaction.guild
        logging.info(f"Slash command '{command_name}' invoked by {user} in {channel} of {guild}")
    await bot.process_application_commands(interaction)


if __name__ == "__main__":
    logging.info("Starting bot...")
    logging.info(f"Guild IDs: {GUILD_IDS}")
    logging.info(f"Pycord version: {discord.__version__}")

    bot.loop.create_task(load_extensions())

    #Register the Lavalink node ready listener
    lavalink_manager.register_node_ready_listener(bot)

    # Connect to Lavalink nodes
    bot.loop.create_task(lavalink_manager.connect_nodes(bot))

    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure as e:
        logging.error(f"Login failed: {e}")
    except discord.errors.HTTPException as e:
        logging.error(f"HTTP error: {e}")
    except discord.errors.GatewayNotFound as e:
        logging.error(f"Gateway not found: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")