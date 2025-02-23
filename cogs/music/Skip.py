import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

class SkipCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="skip", description="Skip the currently playing track and play the next track in queue if available.")
    async def skip(self, ctx: discord.ApplicationContext):
        log_command_invocation(ctx, "skip")
        try:
            vc: wavelink.Player = ctx.voice_client
            if not vc:
                return await ctx.respond("I'm not connected to a voice channel.")

            # Skip the current track.
            skipped_track = await vc.skip(force=True)
            response_message = f"Skipped track: `{skipped_track.title}`\n"

            # If a custom queue exists and is non-empty, play the next track.
            if hasattr(vc, "queue") and not vc.queue.is_empty:
                next_track = vc.queue.get()  # You could also await vc.queue.get_wait() if desired.
                await vc.play(next_track)
                response_message += f"Now playing: `{next_track.title}`"
            else:
                response_message += "No more tracks in queue."

            await ctx.respond(response_message)
        except Exception as e:
            log_error(ctx, "An error occurred in the 'skip' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(SkipCog(bot))

