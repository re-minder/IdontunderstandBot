import os
import logging
from fastapi import FastAPI, Request, HTTPException
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
_initialized = False

# Register the same handlers as in polling mode
ptb_app.add_handler(CommandHandler("start", bot_module.start))
ptb_app.add_handler(CommandHandler("clear", bot_module.clear_video))
ptb_app.add_handler(CommandHandler("status", bot_module.status))
ptb_app.add_handler(MessageHandler(filters.VIDEO, bot_module.store_video_handler))
ptb_app.add_handler(InlineQueryHandler(bot_module.inline_query_handler))
ptb_app.add_error_handler(bot_module.on_error)


@app.get("/")
async def health_root() -> dict:
    # Warm initialization on health check to reduce cold start latency
    global _initialized
    if not _initialized:
        try:
            import time as _t
            start_ns = _t.time()
            await ptb_app.initialize()
            _initialized = True
            init_ms = int((_t.time() - start_ns) * 1000)
            logger.info(f"PTB Application initialized via GET / in {init_ms}ms")
            try:
                state_start_ns = _t.time()
                bot_module.load_state()
                state_ms = int((_t.time() - state_start_ns) * 1000)
                logger.info(f"State loaded on GET / in {state_ms}ms")
            except Exception as exc:
                logger.exception("Failed to load state on GET /", exc_info=exc)
        except Exception as exc:
            logger.exception("Failed to initialize PTB app on GET /", exc_info=exc)
            # Still return ok
    return {"ok": True}

@app.get("/api/bot")
async def health_full() -> dict:
    # Warm initialization on health check to reduce cold start latency
    global _initialized
    if not _initialized:
        try:
            import time as _t
            start_ns = _t.time()
            await ptb_app.initialize()
            _initialized = True
            init_ms = int((_t.time() - start_ns) * 1000)
            logger.info(f"PTB Application initialized via GET /api/bot in {init_ms}ms")
            try:
                state_start_ns = _t.time()
                bot_module.load_state()
                state_ms = int((_t.time() - state_start_ns) * 1000)
                logger.info(f"State loaded on GET /api/bot in {state_ms}ms")
            except Exception as exc:
                logger.exception("Failed to load state on GET /api/bot", exc_info=exc)
        except Exception as exc:
            logger.exception("Failed to initialize PTB app on GET /api/bot", exc_info=exc)
            # Still return ok
    return {"ok": True}


async def _process_webhook(request: Request) -> dict:
    global _initialized
    if not _initialized:
        try:
            await ptb_app.initialize()
            _initialized = True
            logger.info("PTB Application initialized (lazy)")
            # Load persisted state (Redis if configured, else JSON) on cold start
            try:
                bot_module.load_state()
            except Exception as exc:
                logger.exception("Failed to load state on startup", exc_info=exc)
        except Exception as exc:
            logger.exception("Failed to initialize PTB app", exc_info=exc)
            # Still return 200 to avoid Telegram retries storm
            return {"ok": True}
    # Optional secret verification (recommended)
    secret = os.getenv("WEBHOOK_SECRET")
    if secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != secret:
            raise HTTPException(status_code=403, detail="Forbidden")
    # Parse JSON body safely
    try:
        data = await request.json()
    except Exception:
        logger.warning("Webhook received non-JSON body")
        return {"ok": True}

    # Process update with PTB, never bubble errors to Telegram
    try:
        update = Update.de_json(data, ptb_app.bot)
        await ptb_app.process_update(update)
    except Exception as exc:
        logger.exception("Error while processing update", exc_info=exc)
    return {"ok": True}


@app.post("/")
async def webhook_root(request: Request) -> dict:
    return await _process_webhook(request)


@app.post("/api/bot")
async def webhook_full(request: Request) -> dict:
    return await _process_webhook(request)


