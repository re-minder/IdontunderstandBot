from typing import List

from telegram import (
    InlineQuery,
    InlineQueryResultCachedVideo,
    Message,
    Update,
)
from telegram.ext import CallbackContext

from .db import VideoStorage


def handle_start(update: Update, context: CallbackContext, owner_id: int) -> None:
    message: Message = update.message  # type: ignore[assignment]
    if not message:
        return

    if message.from_user and message.from_user.id == owner_id:
        message.reply_text(
            "Hi! Send me a video, and I'll store it. Then anyone can use me inline to send it."
        )
    else:
        message.reply_text(
            "This bot works inline. Type @nihuyaNeUnderstandBot in any chat to send the stored video."
        )


def handle_status(update: Update, context: CallbackContext, storage: VideoStorage) -> None:
    message: Message = update.message  # type: ignore[assignment]
    if not message:
        return

    if storage.has_video():
        message.reply_text("Video is stored")
    else:
        message.reply_text("No video stored")


def handle_owner_video(update: Update, context: CallbackContext, storage: VideoStorage, owner_id: int) -> None:
    message: Message = update.message  # type: ignore[assignment]
    if not message or not message.from_user:
        return

    if message.from_user.id != owner_id:
        # Ignore videos from non-owner users
        return

    video = message.video
    if not video:
        return

    storage.upsert_video(video.file_id)
    message.reply_text("Saved. Inline queries will now return this video.")


def handle_inline_query(update: Update, context: CallbackContext, storage: VideoStorage) -> None:
    inline_query: InlineQuery = update.inline_query  # type: ignore[assignment]
    if not inline_query:
        return

    file_id = storage.get_video_file_id()
    if not file_id:
        inline_query.answer(
            results=[],
            switch_pm_text="No video stored yet. Start me to add one.",
            switch_pm_parameter="start",
            cache_time=2,
            is_personal=True,
        )
        return

    results: List[InlineQueryResultCachedVideo] = [
        InlineQueryResultCachedVideo(
            id="video-1",
            video_file_id=file_id,
            title="Stored video",
            description="Provided by nihuyaNeUnderstandBot",
        )
    ]

    inline_query.answer(results=results, cache_time=2, is_personal=True)


