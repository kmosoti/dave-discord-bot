import logging
import json
import uuid
import sys
import discord

class MinimalJsonFormatter(logging.Formatter):
    def format(self, record):
        # Generate a unique log_id unless one is already provided.
        log_id = record.__dict__.get("error_id", str(uuid.uuid4()))
        # Build a minimal log record with only essential fields.
        log_record = {
            "log_id": log_id,
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage()
        }
        # Only include a few selected extra fields if present.
        for key in ["user_id", "guild_id", "channel_id", "command"]:
            if key in record.__dict__:
                log_record[key] = record.__dict__[key]
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logging(log_file: str = "logs/bot.log") -> None:
    """
    Configure logging to output to both the console and a file in JSON format
    with minimal information.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = MinimalJsonFormatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)
    except FileNotFoundError:
        # Skip file handler setup if the directory doesn't exist.
        pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # Reduce verbosity for noisy modules.
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("wavelink").setLevel(logging.WARNING)

def log_command_invocation(ctx: discord.ApplicationContext, command_name: str):
    """
    Log a command invocation with minimal context.
    If ctx is None, logs without additional context.
    """
    if ctx is None:
        logging.info(f"Command '{command_name}' invoked (no context).")
        return
    extra_fields = {
        "user_id": ctx.author.id,
        "guild_id": ctx.guild.id if ctx.guild else None,
        "channel_id": ctx.channel.id if ctx.channel else None,
        "command": command_name,
    }
    logging.info(f"Command '{command_name}' invoked.", extra=extra_fields)

def log_error(error_message: str, ctx: discord.ApplicationContext = None):
    """
    Log an error with a unique error_id and minimal context.
    If ctx is None, only the error message is logged.
    """
    extra_fields = {"error_id": str(uuid.uuid4())}
    if ctx:
        extra_fields.update({
            "user_id": ctx.author.id,
            "guild_id": ctx.guild.id if ctx.guild else None,
            "channel_id": ctx.channel.id if ctx.channel else None,
            "command": ctx.command.name if ctx.command else "N/A",
        })
    logging.error(error_message, extra=extra_fields)

# Example usage:
if __name__ == "__main__":
    setup_logging()
    logging.info("This is an info log.")
    logging.error("This is an error log.")
