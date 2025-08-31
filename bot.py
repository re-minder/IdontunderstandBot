#!/usr/bin/env python3
"""
Video Sending Bot - Main Application
"""

import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, InlineQueryHandler
from telegram import Update

from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from handlers.command_handlers import start_command, help_command, clear_video, video_status
from handlers.video_handlers import store_video
from handlers.inline_handlers import inline_query

# Configure logging
logging.basicConfig(
    format=LOG_FORMAT,
    level=getattr(logging, LOG_LEVEL),
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    logger.info("Starting Video Sending Bot...")
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clearVideo", clear_video))
    application.add_handler(CommandHandler("videoStatus", video_status))
    
    # Add video handler
    application.add_handler(MessageHandler(filters.VIDEO, store_video))
    
    # Add inline query handler
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Start the bot
    logger.info("Video Sending Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
