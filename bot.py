#!/usr/bin/env python3
"""
Telegram Bot - Main Application
"""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, InlineQueryHandler
from telegram import Update

from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from handlers.command_handlers import start_command, help_command, status_command, echo
from handlers.video_handlers import store_video, send_the_video, clear_video, video_status
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
    logger.info("Starting Telegram Bot...")
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Add video command handlers
    application.add_handler(CommandHandler("sendTheVideo", send_the_video))
    application.add_handler(CommandHandler("clearVideo", clear_video))
    application.add_handler(CommandHandler("videoStatus", video_status))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.VIDEO, store_video))
    
    # Add inline query handler
    application.add_handler(InlineQueryHandler(inline_query))
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
