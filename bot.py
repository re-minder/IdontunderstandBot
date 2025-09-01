#!/usr/bin/env python3
"""
Simple Video Sending Bot
"""

import os
import json
import logging
import time
from dotenv import load_dotenv
from telegram import Update, InlineQueryResultVideo, InputTextMessageContent, InputFile, InlineQueryResultCachedVideo, InlineQueryResultArticle
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters
from telegram.error import NetworkError

# Optional durable KV (Upstash Redis)
REDIS_URL = os.getenv('UPSTASH_REDIS_REST_URL')
REDIS_TOKEN = os.getenv('UPSTASH_REDIS_REST_TOKEN')
redis_client = None
if REDIS_URL and REDIS_TOKEN:
    try:
        from upstash_redis import Redis
        redis_client = Redis(url=REDIS_URL, token=REDIS_TOKEN)
    except Exception as exc:
        # If client fails to init, fall back to JSON
        redis_client = None
        logging.getLogger(__name__).error(f"Failed to init Redis client: {exc}")

# Load environment variables
load_dotenv()

# Configure logging (avoid file writes on serverless read-only FS)
handlers_list = [logging.StreamHandler()]
try:
    handlers_list.append(logging.FileHandler('bot.log'))
except OSError:
    # Read-only FS (e.g., Vercel). Skip file logging.
    pass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
    handlers=handlers_list
)
logger = logging.getLogger(__name__)
# Suppress noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Global variable to store the video
stored_video = None

# Owner user id (only owner can set/clear video)
OWNER_ID_STR = os.getenv('OWNER_ID')
OWNER_ID = int(OWNER_ID_STR) if OWNER_ID_STR and OWNER_ID_STR.isdigit() else None

STATE_FILE_PATH = 'state.json'

def load_state():
    """Load stored state from disk into memory."""
    global stored_video
    # Prefer Redis if available
    if redis_client is not None:
        try:
            value = redis_client.get('stored_video')
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            stored_video_local = value if value not in (None, "") else None
            stored_video = stored_video_local
            logger.info("State loaded from Redis")
            return
        except Exception as exc:
            logger.error(f"Failed to load state from Redis: {exc}")
    # Fallback to JSON file
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
    # Prefer Redis if available
    if redis_client is not None:
        try:
            # Store empty string to represent None
            value = stored_video if stored_video is not None else ""
            redis_client.set('stored_video', value)
            logger.info("State saved to Redis")
            return
        except Exception as exc:
            logger.error(f"Failed to save state to Redis: {exc}")
    # Fallback to JSON file (may be ephemeral in serverless)
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
    logger.info("Video stored successfully")
    save_state()
    
    await update.message.reply_text(
        f"✅ Video stored! Use @{context.bot.username} in any chat to send it."
    )

async def inline_query_handler(update: Update, context):
    """Handle inline queries."""
    global stored_video
    
    logger.info("Inline query received")
    logger.info(f"Inline query - stored video: {stored_video}")
    logger.info(f"Inline query - stored video type: {type(stored_video)}")
    logger.info(f"Inline query - stored video is None: {stored_video is None}")
    _start_inline = time.time()
    
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
        # Add a small time bucket to the result id to mitigate Telegram client cache per chat
        time_bucket = int(time.time() // 5)  # 5-second buckets to reduce stale results even more
        results = [
            # Instant lightweight fallback so the client always renders something
            InlineQueryResultArticle(
                id=f"fallback_{int(time.time())}",
                title="Loading video… tap if it doesn't appear",
                description="This shows instantly; try again if video is still loading",
                input_message_content=InputTextMessageContent(
                    "If the video didn’t load, wait a second and type the bot handle again."
                ),
            ),
            InlineQueryResultCachedVideo(
                id=f"vid_{stored_video[-32:]}_{time_bucket}",
                title="Send stored video",
                description="Click to send the stored video",
                video_file_id=stored_video
            )
        ]
    
    try:
        await update.inline_query.answer(results, cache_time=0, is_personal=True)
        _elapsed_ms = int((time.time() - _start_inline) * 1000)
        logger.info(f"Inline answer sent in {_elapsed_ms}ms (has_video={bool(stored_video)})")
        if _elapsed_ms > 4000:
            logger.warning(f"Slow inline answer: {_elapsed_ms}ms (risk of client timeout)")
    except NetworkError as exc:
        if "Event loop is closed" in str(exc):
            _elapsed_ms = int((time.time() - _start_inline) * 1000)
            logger.warning(f"Inline answer aborted due to shutdown after {_elapsed_ms}ms")
            return
        raise

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
    # By default, avoid owner notifications in serverless/webhook mode to prevent noisy errors
    if os.getenv('ENABLE_OWNER_NOTIFICATIONS') == '1' and OWNER_ID is not None:
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=f"⚠️ Bot error: {context.error}")
        except NetworkError as exc:
            # Ignore teardown errors from serverless runtime
            if "Event loop is closed" in str(exc):
                return
            raise
        except RuntimeError as exc:
            if "Event loop is closed" in str(exc):
                return
            raise

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
