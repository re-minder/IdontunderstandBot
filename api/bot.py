import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters

# Import handlers and state from existing bot module
import bot as bot_module

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
# Suppress noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("telegram").setLevel(logging.WARNING)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not found in environment variables")

app = FastAPI()

# Create a single Application instance reused across warm invocations
ptb_app = Application.builder().token(TOKEN).build()

# Register the same handlers as in polling mode
ptb_app.add_handler(CommandHandler("start", bot_module.start))
ptb_app.add_handler(CommandHandler("clear", bot_module.clear_video))
ptb_app.add_handler(CommandHandler("status", bot_module.status))
ptb_app.add_handler(MessageHandler(filters.VIDEO, bot_module.store_video_handler))
ptb_app.add_handler(InlineQueryHandler(bot_module.inline_query_handler))
ptb_app.add_error_handler(bot_module.on_error)


@app.on_event("startup")
async def on_startup() -> None:
    # Initialize and start PTB application once on cold start
    await ptb_app.initialize()
    await ptb_app.start()
    logger.info("PTB Application initialized")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    # Graceful shutdown
    await ptb_app.stop()
    await ptb_app.shutdown()


@app.get("/")
async def health() -> dict:
    return {"ok": True}


@app.post("/")
async def webhook(request: Request) -> dict:
    data = await request.json()
    update = Update.de_json(data, ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}


