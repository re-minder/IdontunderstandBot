from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# Global variable to store the video file_id
stored_video = None

async def store_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Store the video sent by the user."""
    global stored_video
    
    if not update.message.video:
        await update.message.reply_text("❌ Please send a video file to store.")
        return
    
    stored_video = update.message.video.file_id
    await update.message.reply_text("✅ Video stored successfully! Use @" + context.bot.username + " in any chat to send it.")
