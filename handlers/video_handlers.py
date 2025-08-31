from telegram import Update
from telegram.ext import ContextTypes
import logging
import json
import os

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
    await update.message.reply_text("✅ Video stored successfully! Use /sendTheVideo <user_id> to send it to someone.")

async def send_the_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the stored video to a specific user in private chat."""
    global stored_video
    
    if not stored_video:
        await update.message.reply_text("❌ No video stored. Please send a video first.")
        return
    
    # Check if user_id is provided
    if not context.args:
        await update.message.reply_text("❌ Please provide a user ID. Usage: /sendTheVideo <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a valid number.")
        return
    
    try:
        # Send the video to the specified user in private chat
        await context.bot.send_video(
            chat_id=user_id,
            video=stored_video,
            caption="Video sent via bot"
        )
        
        await update.message.reply_text(f"✅ Video sent successfully to user {user_id} in private chat!")
        logger.info(f"Video sent to user {user_id} by {update.effective_user.id}")
        
    except Exception as e:
        if "Forbidden" in str(e) or "bot was blocked" in str(e).lower():
            error_msg = f"❌ Cannot send video to user {user_id}. The user must start a chat with the bot first by sending /start to the bot."
        elif "chat not found" in str(e).lower():
            error_msg = f"❌ Cannot send video to user {user_id}. The user has not started a conversation with the bot."
        else:
            error_msg = f"❌ Failed to send video to user {user_id}. Error: {str(e)}"
        await update.message.reply_text(error_msg)
        logger.error(f"Failed to send video to user {user_id}: {e}")

async def clear_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the stored video."""
    global stored_video
    
    stored_video = None
    await update.message.reply_text("🗑️ Stored video cleared.")

async def video_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if a video is stored."""
    global stored_video
    
    if stored_video:
        await update.message.reply_text("✅ A video is currently stored and ready to send.")
    else:
        await update.message.reply_text("❌ No video is currently stored.")
