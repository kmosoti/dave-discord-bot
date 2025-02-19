import typing
import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

class PlayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(name="play", description="Play a song from a search query or enqueue if something is already playing.")
    async def play(self, ctx: discord.ApplicationContext, search: str):
        """Handles playing a song immediately or adding it to the queue if a song is playing."""
        log_command_invocation(ctx, "play")

        try:
            # Ensure the user is in a voice channel.
            if not ctx.author.voice or not ctx.author.voice.channel:
                return await ctx.respond("You must be in a voice channel to use this command.")

            # Connect to the voice channel if not already connected.
            vc: wavelink.Player = typing.cast(wavelink.Player, ctx.voice_client)
            if not vc:
                vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

            if vc.channel.id != ctx.author.voice.channel.id:
                return await ctx.respond("You must be in the same voice channel as the bot.")

            # Search for the track.
            try:
                songs = await wavelink.Playable.search(search)
            except wavelink.LavalinkLoadException as e:
                log_error(ctx, "Failed to load tracks", exception=e)
                return await ctx.respond("An error occurred while searching for the song.")

            if not songs:
                return await ctx.respond("No song found.")

            song = songs[0]

            # Ensure the player has a queue.
            if not hasattr(vc, "queue"):
                vc.queue = wavelink.Queue()  # Initialize the queue

            if not vc.playing:
                # If nothing is playing, start playing immediately
                await vc.play(song)
                log_command_invocation(ctx, f"Now playing: {song.title}")
                await ctx.respond(f"Now playing: `{song.title}`")
            else:
                # Otherwise, enqueue the song.
                vc.queue.put(song)
                log_command_invocation(ctx, f"Added to queue: {song.title}")
                await ctx.respond(f"Added to queue: `{song.title}`")

        except Exception as e:
            log_error(ctx, "An error occurred in 'play' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(PlayCog(bot))
