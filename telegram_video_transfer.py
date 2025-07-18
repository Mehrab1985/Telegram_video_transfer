# telegram_video_transfer.py
# This bot listens for messages containing a command and a URL,
# then transfers the video from that URL to a specified channel.

# --- Prerequisites ---
# 1. Install the library: pip install python-telegram-bot --upgrade
# 2. Get a Bot Token from BotFather on Telegram.
# 3. Get the Chat ID of your channel or group.
#    - For a public channel, it's the @username (e.g., '@mychannel').
#    - For a private channel/group, you can get it from a bot like @userinfobot. It will be a negative number (e.g., -1001234567890).
# 4. Add your bot to the channel as an Administrator with permission to 'Post Messages'.

import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
# The bot now reads credentials from environment variables for security.
# You will set these variables in your hosting environment (e.g., Railway).
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHANNEL_ID = os.environ.get("TARGET_CHANNEL_ID")

# --- Logging Setup ---
# Enable logging to see errors and bot activity.
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set a higher log level for httpx to avoid spammy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Debugging Step ---
# Let's print the status of the variables the script sees.
# This will show up in your Railway deployment logs.
# For security, we do not print the actual token, just whether it was found.
logger.info(f"--- Environment Variable Check ---")
logger.info(f"BOT_TOKEN found: {'Yes' if BOT_TOKEN else 'No'}")
logger.info(f"TARGET_CHANNEL_ID found: {'Yes' if TARGET_CHANNEL_ID else 'No'}")
logger.info(f"------------------------------------")


# --- Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Sends a welcome message explaining how to use the bot.
    """
    user = update.effective_user
    welcome_message = (
        f"👋 Hi {user.first_name}!\n\n"
        "I am the Telegram Video Transfer bot.\n"
        "I can transfer videos to a channel directly from a web link.\n\n"
        "To use me, send a message in this format:\n"
        "`/transfer <direct_video_url>`\n\n"
        "For example:\n"
        "`/transfer https://example.com/videos/my_awesome_video.mp4`"
    )
    await update.message.reply_html(welcome_message)


async def transfer_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /transfer command.
    Parses the URL and sends the video to the target channel.
    """
    if not context.args:
        await update.message.reply_text("❌ Please provide a URL after the /transfer command.")
        return

    video_url = context.args[0]
    logger.info(f"Received transfer request for URL: {video_url}")

    await update.message.reply_text("⏳ Got it! Starting the transfer process...")

    try:
        await context.bot.send_video(
            chat_id=TARGET_CHANNEL_ID,
            video=video_url,
            caption="Video transferred via the URL Bot! 🚀",
            supports_streaming=True
        )
        logger.info(f"Successfully transferred video from {video_url} to {TARGET_CHANNEL_ID}")
        await update.message.reply_text("✅ Success! The video has been transferred to the channel.")

    except Exception as e:
        logger.error(f"Failed to transfer video from {video_url}. Error: {e}")
        error_message = (
            "😥 An error occurred.\n\n"
            "Please check a few things:\n"
            "1. Is the link a **direct** link to a video file (e.g., .mp4, .mov)?\n"
            "2. Is the video file accessible and not too large?\n"
            f"3. Is the bot an admin in the channel `{TARGET_CHANNEL_ID}`?\n\n"
            f"Error details: `{e}`"
        )
        await update.message.reply_html(error_message)


# --- Main Bot Execution ---

def main() -> None:
    """Start the bot."""
    # Pre-flight check for environment variables.
    # The debug logs above will tell us why this might fail.
    if not BOT_TOKEN or not TARGET_CHANNEL_ID:
        logger.error("FATAL: One or both environment variables are missing. Bot will not start.")
        return
        
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("transfer", transfer_video_command))

    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

# --- Version 4: Added Debug Logging ---
