import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

class VolumeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="volume", description="Set the playback volume (0-1000).")
    async def volume(self, ctx: discord.ApplicationContext, level: int):
        log_command_invocation(ctx, "volume")
        try:
            vc: wavelink.Player = ctx.voice_client
            if not vc:
                return await ctx.respond("I'm not connected to a voice channel.")
            
            # Ensure the volume level is within acceptable bounds.
            if level < 0 or level > 1000:
                return await ctx.respond("Volume must be between 0 and 1000.")
            
            await vc.set_volume(level)
            await ctx.respond(f"Volume set to {level}%.")
        except Exception as e:
            log_error(ctx, "An error occurred in the 'volume' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(VolumeCog(bot))
