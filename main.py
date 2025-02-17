import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # INFO is chatty without being overwhelming
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables from the .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logging.error("DISCORD_TOKEN environment variable not set.")
    exit(1)

# Define the bot's intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f"{bot.user} is connected to Discord!")

@bot.event
async def on_message(message):
    """
    Log every message that passes through.
    To avoid flooding the logs with our own messages, we log them at DEBUG.
    """
    if message.author == bot.user:
        logging.debug(f"Bot sent a message in #{message.channel}: {message.content}")
    else:
        logging.info(f"Message from {message.author} in #{message.channel}: {message.content}")
    
    # Ensure commands still get processed
    await bot.process_commands(message)

@bot.command(name="hello")
async def hello(ctx):
    response = "Hello from DAVE!"
    await ctx.send(response)
    logging.info(f"Sent response: '{response}' in #{ctx.channel}")

@bot.event
async def on_command_error(ctx, error):
    logging.error(f"Error in command '{ctx.command}': {error}")

if __name__ == "__main__":
    bot.run(TOKEN)
