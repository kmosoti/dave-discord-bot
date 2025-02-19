import logging
import json
import uuid
import sys
import discord

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Generate a unique log_id unless one is already provided in the record.
        log_id = record.__dict__.get("error_id", str(uuid.uuid4()))
        # Build the base log record.
        log_record = {
            "log_id": log_id,
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Merge extra keys from the record (if any) at the same level.
        standard_keys = {
            "error_id", "asctime", "levelname", "name", "msg", "args", "exc_info", "stack_info"
        }
        for key, value in record.__dict__.items():
            if key not in standard_keys:
                log_record[key] = value
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_trace"] = self.formatStack(record.stack_info)
        return json.dumps(log_record)

def setup_logging(log_file: str = "logs/bot.log") -> None:
    """
    Configure logging to output to both the console and a file in JSON format.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = JsonFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.getLogger("discord.gateway").setLevel(logging.WARNING)

def log_command_invocation(ctx: discord.ApplicationContext, command_name: str):
    """
    Log a command invocation with additional context.
    """
    extra_fields = {
        "user_id": ctx.author.id,
        "guild_id": ctx.guild.id if ctx.guild else None,
        "channel_id": ctx.channel.id if ctx.channel else None,
        "command": command_name,
    }
    logging.info(f"Command '{command_name}' invoked.", extra=extra_fields)

def log_error(error_message: str, ctx: discord.ApplicationContext = None):
    """
    Log an error with a unique error_id and optional context.
    The unique error_id is generated here, so you don't have to pass it in.
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
