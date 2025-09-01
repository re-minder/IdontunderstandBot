#!/usr/bin/env python3
"""
Simple Video Sending Bot
"""

import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultVideo, InputTextMessageContent, InputFile, InlineQueryResultCachedVideo
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters

# Load environment variables
load_dotenv()

# Configure logging to file
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global variable to store the video
stored_video = None

# Owner user id (only owner can set/clear video)
OWNER_ID_STR = os.getenv('OWNER_ID')
OWNER_ID = int(OWNER_ID_STR) if OWNER_ID_STR and OWNER_ID_STR.isdigit() else None

STATE_FILE_PATH = 'state.json'

def load_state():
    """Load stored state from disk into memory."""
    global stored_video
    try:
        if os.path.exists(STATE_FILE_PATH):
            with open(STATE_FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                stored_video = data.get('stored_video')
                logger.info("State loaded from disk")
    except Exception as exc:
        logger.error(f"Failed to load state: {exc}")

def save_state():
    """Persist current state to disk."""
    try:
        with open(STATE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump({'stored_video': stored_video}, f)
        logger.info("State saved to disk")
    except Exception as exc:
        logger.error(f"Failed to save state: {exc}")

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text(
        "👋 Hi! Send me a video to store it, then use @nihuyaNeUnderstandBot in any chat to send it!"
    )

async def store_video_handler(update: Update, context):
    """Store the video sent by user."""
    global stored_video
    # Owner-only guard
    if OWNER_ID is not None:
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ Only the owner can update the stored video.")
            return
    
    if not update.message.video:
        await update.message.reply_text("❌ Please send a video file.")
        return
    
    stored_video = update.message.video.file_id
    logger.info(f"Video stored: {stored_video}")
    save_state()
    
    await update.message.reply_text(
        f"✅ Video stored! Use @{context.bot.username} in any chat to send it."
    )

async def inline_query_handler(update: Update, context):
    """Handle inline queries."""
    global stored_video
    
    logger.info(f"Inline query - stored video: {stored_video}")
    logger.info(f"Inline query - stored video type: {type(stored_video)}")
    logger.info(f"Inline query - stored video is None: {stored_video is None}")
    
    if not stored_video:
        # No video stored
        results = [
            InlineQueryResultVideo(
                id="no_video",
                title="No video stored",
                description="Send a video to the bot first",
                video_url="https://example.com/placeholder.mp4",
                mime_type="video/mp4",
                thumbnail_url="https://example.com/placeholder.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=f"❌ No video stored. Send a video to @{context.bot.username} first."
                )
            )
        ]
    else:
        # Video is stored
        results = [
            InlineQueryResultCachedVideo(
                id=f"vid_{stored_video[-32:]}",
                title="Send stored video",
                description="Click to send the stored video",
                video_file_id=stored_video
            )
        ]
    
    await update.inline_query.answer(results, cache_time=0, is_personal=True)

async def clear_video(update: Update, context):
    """Clear stored video."""
    global stored_video
    # Owner-only guard
    if OWNER_ID is not None:
        user_id = update.effective_user.id if update.effective_user else None
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ Only the owner can clear the stored video.")
            return
    stored_video = None
    save_state()
    await update.message.reply_text("🗑️ Video cleared.")

async def status(update: Update, context):
    """Check if video is stored."""
    global stored_video
    if stored_video:
        video_tail = stored_video[-8:] if isinstance(stored_video, str) else ""
        owner_info = f" (owner {OWNER_ID})" if OWNER_ID is not None else ""
        await update.message.reply_text(f"✅ Video is stored and ready to send. id…{video_tail}{owner_info}")
    else:
        await update.message.reply_text("❌ No video stored.")

from telegram.ext import ContextTypes

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler to log and notify owner."""
    logger.exception("Exception while handling an update", exc_info=context.error)
    try:
        if OWNER_ID is not None:
            await context.bot.send_message(chat_id=OWNER_ID, text=f"⚠️ Bot error: {context.error}")
    except Exception as notify_exc:
        logger.error(f"Failed to notify owner about error: {notify_exc}")

def main():
    """Start the bot."""
    # Get bot token
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    # Load state from disk
    load_state()
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_video))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(MessageHandler(filters.VIDEO, store_video_handler))
    application.add_handler(InlineQueryHandler(inline_query_handler))
    application.add_error_handler(on_error)
    
    # Start the bot
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
