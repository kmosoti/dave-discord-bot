import pathlib
import json
import logging
import discord
import asyncio
from discord.ext import commands

# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(f"logs/bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

# Load configuration from data/config.json
config_path = pathlib.Path("data/config.json")
if not config_path.exists():
    logging.error("Configuration file not found.")
    exit(1)

with config_path.open("r") as f:
    config = json.load(f)

TOKEN = config.get("DISCORD_TOKEN")
if not TOKEN:
    logging.error("DISCORD_TOKEN not set in configuration file.")
    exit(1)

# Read guild IDs list from configuration (for testing, these guilds will update instantly)
GUILD_IDS = config.get("GUILD_IDS", [])

# Define the bot's intents
intents = discord.Intents.default()
intents.message_content = True

# Instantiate the bot with our intents and debug_guilds for instant command registration
bot = discord.Bot(intents=intents, debug_guilds=GUILD_IDS)

# Optionally attach config to the bot for easy access in your cogs
bot.config = config

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
