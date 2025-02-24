import typing
import discord
from discord.ext import commands
import wavelink
from utils.discord_logger import log_command_invocation, log_error

# Helper function to connect to the user's voice channel.
async def connect_to_voice_channel(ctx: discord.ApplicationContext) -> wavelink.Player:
    if not ctx.author.voice or not ctx.author.voice.channel:
        raise ValueError("You must be in a voice channel to use this command.")

    # Use the existing voice client if available.
    vc: wavelink.Player = typing.cast(wavelink.Player, ctx.voice_client)
    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        vc.queue = wavelink.Queue()  # Initialize the queue immediately.
    elif vc.channel.id != ctx.author.voice.channel.id:
        raise ValueError("You must be in the same voice channel as the bot.")

    return vc

# Helper function to perform a search and return the first track.
async def search_for_track(query: str) -> wavelink.Playable:
    if query.startswith("http"):
        songs = await wavelink.Playable.search(query)
    try:
        songs = await wavelink.Playable.search(query, source=wavelink.TrackSource.SoundCloud)
    except wavelink.LavalinkLoadException as e:
        raise RuntimeError("Failed to load tracks") from e

    if not songs:
        return None

    # Return the first track from the search results.
    return songs[0]

async def play_song(vc: wavelink.Player, song: wavelink.Playable, ctx: discord.ApplicationContext) -> None:
    if not vc.playing:
        try:
            await vc.play(song)
            log_command_invocation(ctx, f"Now playing: {song.title}")
        except Exception as e:
            log_error(ctx, f"An error occurred while playing a song", exception=e)
            log_command_invocation(ctx, f"An error occurred while playing")
    else:
        vc.queue.put(song)

async def queue_song(vc: wavelink.Player, song: wavelink.Playable, ctx: discord.ApplicationContext) -> None:
    try:
        vc.queue.put(song)
        log_command_invocation(ctx, f"Added to queue: {song.title}")
    except Exception as e:
        log_error(ctx, f"An error occurred while adding to queue", exception=e)
        log_command_invocation(ctx, f"An error occurred while adding to queue")

class PlayCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player: wavelink.Player = payload.player
        # Only advance if the track ended normally.
        if payload.reason == "finished" and hasattr(player, "queue") and not player.queue.is_empty:
            next_track = player.queue.get()  # You could also await player.queue.get_wait()
            await player.play(next_track)

    @discord.slash_command(
    name="play", 
    description="Play a song from a search query (SoundCloud by default) or enqueue it."
    )
    async def play(self, ctx: discord.ApplicationContext, search: str):
        """
        Searches for and plays a song based on your query.
        
        - If you provide a URL, it plays that track directly.
        - If you provide a plain search query, it uses SoundCloud search (since YouTube search is disabled in your Lavalink config).
        
        If a song is already playing, the new track is added to the queue.
        """
        log_command_invocation(ctx, "play")

        try:
            # Use the helper to connect to the voice channel.
            vc = await connect_to_voice_channel(ctx)
            # Use the helper to search for a track.
            song = await search_for_track(search)

            if not vc.playing:
                await play_song(vc, song, ctx)
                await ctx.respond(f"Now playing: `{song.title}`")
            else:
                await queue_song(vc, song, ctx)
                await ctx.respond(f"Added to queue: `{song.title}`")
        except Exception as e:
            log_error(ctx, "An error occurred in 'play' command", exception=e)
            await ctx.respond("An error occurred while processing your request.")

def setup(bot: commands.Bot):
    bot.add_cog(PlayCog(bot))
