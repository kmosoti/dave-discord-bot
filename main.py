import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file located in the repository root
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Define the bot's intents
intents = discord.Intents.default()
# Uncomment if needed:
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is connected to Discord!")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello from DAVE!")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set.")
    else:
        bot.run(TOKEN)
