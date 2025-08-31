from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")
    
    welcome_message = f"""
👋 Hello {user.first_name}! 

Send me a video to store it, then use @{context.bot.username} in any chat to send it.
    """
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = f"""
📹 **Video Bot Commands:**

/start - Start the bot
/help - Show this help message
/clearVideo - Clear stored video
/videoStatus - Check if video is stored

💬 **Inline Usage:**
- Type `@{context.bot.username}` in any chat to send the stored video
- Works in private chats, groups, and channels
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def clear_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the stored video."""
    import handlers.video_handlers
    handlers.video_handlers.stored_video = None
    
    await update.message.reply_text("🗑️ Stored video cleared.")

async def video_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check if a video is stored."""
    import handlers.video_handlers
    
    if handlers.video_handlers.stored_video:
        await update.message.reply_text("✅ A video is currently stored and ready to send.")
    else:
        await update.message.reply_text("❌ No video is currently stored.")
