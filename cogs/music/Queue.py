import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

class QueueCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="queue", description="Display the current song queue and what is currently playing.")
    async def queue(self, ctx: discord.ApplicationContext):
        log_command_invocation(ctx, "queue")
        try:
            vc: wavelink.Player = ctx.voice_client
            if not vc:
                return await ctx.respond("I'm not connected to a voice channel.")

            message = ""

            # Show the currently playing track if available.
            if vc.current:
                message += f"**Currently Playing:** {vc.current.title}\n\n"
            else:
                message += "**Currently Playing:** Nothing\n\n"

            # Then show the rest of the queue.
            if not hasattr(vc, "queue") or vc.queue.is_empty:
                message += "The queue is empty."
            else:
                message += "**Current Queue:**\n"
                queue_list = list(vc.queue)
                for idx, track in enumerate(queue_list, start=1):
                    message += f"{idx}. {track.title}\n"

            await ctx.respond(message)
        except Exception as e:
            log_error(ctx, "An error occurred in 'queue' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(QueueCog(bot))
