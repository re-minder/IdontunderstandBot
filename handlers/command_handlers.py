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

Welcome to the Telegram Bot! 

I'm here to help you. Use /help to see available commands.
    """
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = """
🤖 **Available Commands:**

/start - Start the bot and get a welcome message
/help - Show this help message
/status - Check bot status

📹 **Video Commands:**
- Send a video to store it
- /sendTheVideo <user_id> - Send stored video to a user
- /clearVideo - Clear stored video
- /videoStatus - Check if video is stored

💬 **Inline Usage:**
- Type `@your_bot_username` in any chat to send the stored video
- Works in private chats, groups, and channels

**Features:**
- Basic command handling
- Message processing
- Video forwarding system
- Extensible architecture

For more information, check the README file.
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    status_message = """
✅ **Bot Status:**
- Bot is running
- All systems operational
- Ready to process commands
    """
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)
