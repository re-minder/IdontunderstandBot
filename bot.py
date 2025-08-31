#!/usr/bin/env python3
"""
Telegram Bot - Main Application
"""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update

from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT
from handlers.command_handlers import start_command, help_command, status_command, echo

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
    
    # Add message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
