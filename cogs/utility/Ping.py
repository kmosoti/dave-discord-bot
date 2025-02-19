import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="ping",
        description="Replies with Pong! and shows bot latency."
    )
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f"Pong! 🏓 Latency: {round(self.bot.latency * 1000)}ms")

def setup(bot: commands.Bot):
    """Proper async setup function for Pycord 2.6.1"""
    bot.add_cog(Ping(bot))
