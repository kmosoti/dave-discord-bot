import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

class StopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="stop", description="Stop the current playback and clear the queue.")
    async def stop(self, ctx: discord.ApplicationContext):
        log_command_invocation(ctx, "stop")
        try:
            vc: wavelink.Player = ctx.voice_client
            if not vc:
                return await ctx.respond("I'm not connected to a voice channel.")

            # Stop the current track (stop() is an alias to skip() with force=True)
            stopped_track = await vc.stop(force=True)
            
            # Clear the queue if it exists
            if hasattr(vc, "queue"):
                vc.queue.clear()

            await ctx.respond("Playback stopped and queue cleared.")
        except Exception as e:
            log_error(ctx, "An error occurred in 'stop' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(StopCog(bot))
