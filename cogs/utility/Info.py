#Slash command that returns verbose information about the bot and the server it's running on including latency. As well as the user who invoked the command.
import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="info",
        description="Shows information about the bot and the server it's running on."
    )
    async def info(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="Bot Information", color=0x7289DA)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Bot Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="User Name", value=ctx.author.name, inline=True)
        embed.add_field(name="User ID", value=ctx.author.id, inline=True)
        await ctx.respond(embed=embed)

def setup(bot: commands.Bot):
    """Proper async setup function for Pycord 2.6.1"""
    bot.add_cog(Info(bot))