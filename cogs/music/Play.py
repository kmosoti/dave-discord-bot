import typing
import discord
from discord.ext import commands
import wavelink
import asyncio
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
        vc.inactive_timeout = 60  # ADDED: Set built-in inactivity timeout to 60 seconds.
        # Removed manual scheduling of inactivity disconnect:
        # vc.inactive_task = asyncio.create_task(schedule_inactivity_disconnect(vc))
    elif vc.channel.id != ctx.author.voice.channel.id:
        raise ValueError("You must be in the same voice channel as the bot.")
    
    # Ensure inactive_timeout is set when reusing the voice client.
    vc.inactive_timeout = 60

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

# Removed: schedule_inactivity_disconnect function is no longer needed because we use the built-in inactive_timeout.
# async def schedule_inactivity_disconnect(player: wavelink.Player):
#     await asyncio.sleep(60)
#     if not player.playing:
#         log_command_invocation(None, "Inactivity timeout reached. Disconnecting from voice.")
#         await player.disconnect()

async def play_song(vc: wavelink.Player, song: wavelink.Playable, ctx: discord.ApplicationContext) -> None:
    # Cancel any manual inactivity disconnect tasks if they exist.
    if hasattr(vc, "inactive_task") and not vc.inactive_task.done():
        vc.inactive_task.cancel()
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
        # Only advance if the track ended normally and there is a queue.
        if payload.reason.lower() == "finished" and hasattr(player, "queue") and not player.queue.is_empty:
            next_track = player.queue.get()  # or await player.queue.get_wait() if needed
            await player.play(next_track)
            # Cancel any pending manual inactivity disconnect.
            if hasattr(player, "inactive_task") and not player.inactive_task.done():
                player.inactive_task.cancel()
        # Removed manual scheduling of inactivity disconnect.
        # else:
        #     if not player.playing:
        #         player.inactive_task = asyncio.create_task(schedule_inactivity_disconnect(player))

    # ADDED: Event listener for built-in inactivity timeout.
    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        log_command_invocation(None, "Inactive timeout reached. Disconnecting from voice.")
        await player.disconnect()

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
