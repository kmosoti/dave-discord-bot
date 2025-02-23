import logging
import wavelink
import discord

async def connect_nodes(bot: discord.Bot):
    """Connect to our Lavalink nodes."""
    await bot.wait_until_ready()  # Wait until the bot is ready

    lavalink_config = bot.config["LAVALINK"]
    host = lavalink_config.get("LAVALINK_HOST", "http://127.0.0.1")
    port = lavalink_config.get("LAVALINK_PORT", 2333)
    password = lavalink_config.get("LAVALINK_PASSWORD")
    uri = f"{host}:{port}"
    nodes = [
        wavelink.Node(
            identifier="Node1",       # Unique identifier for the node
            uri=uri,  # Lavalink server URI (ensure protocol and port are correct)
            password=password
        )
    ]

    try:
        await wavelink.Pool.connect(nodes=nodes, client=bot)
        logging.info("Lavalink nodes connected successfully.")
    except Exception as e:
        logging.error(f"Failed to connect Lavalink nodes: {e}")

def register_node_ready_listener(bot: discord.Bot):
    """Register an event listener to log when a Lavalink node is ready."""
    @bot.event
    async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
        logging.info(f"Node with ID {payload.session_id} has connected")
        logging.info(f"Resumed session: {payload.resumed}")
