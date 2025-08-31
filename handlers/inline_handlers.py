from telegram import Update, InlineQueryResultVideo, InputTextMessageContent
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# Import the video_handlers module to access stored_video
import handlers.video_handlers

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries."""
    query = update.inline_query.query
    
    if not handlers.video_handlers.stored_video:
        # No video stored
        results = [
            InlineQueryResultVideo(
                id="1",
                title="No video stored",
                description="Send a video to the bot first to store it",
                video_url="https://example.com/placeholder.mp4",
                mime_type="video/mp4",
                thumbnail_url="https://example.com/placeholder.jpg",
                input_message_content=InputTextMessageContent(
                    message_text=f"❌ No video stored. Send a video to @{context.bot.username} first."
                )
            )
        ]
    else:
        # Video is stored, offer to send it
        results = [
            InlineQueryResultVideo(
                id="1",
                title="Send stored video",
                description="Click to send the stored video in this chat",
                video_file_id=handlers.video_handlers.stored_video,
                input_message_content=InputTextMessageContent(
                    message_text="📹 Video sent via inline bot"
                )
            )
        ]
    
    await update.inline_query.answer(results)
