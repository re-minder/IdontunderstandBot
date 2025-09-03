import logging
from functools import partial

from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    InlineQueryHandler,
)

from .config import load_config
from .db import VideoStorage
from .handlers import (
    handle_inline_query,
    handle_owner_video,
    handle_start,
    handle_status,
)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def main() -> None:
    configure_logging()
    config = load_config()
    storage = VideoStorage(config.database_path)

    updater = Updater(token=config.bot_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", partial(handle_start, owner_id=config.owner_id)))
    dispatcher.add_handler(CommandHandler("status", partial(handle_status, storage=storage)))
    dispatcher.add_handler(MessageHandler(Filters.video, partial(handle_owner_video, storage=storage, owner_id=config.owner_id)))
    dispatcher.add_handler(InlineQueryHandler(partial(handle_inline_query, storage=storage)))

    def error_handler(update, context: CallbackContext) -> None:  # type: ignore[no-redef]
        logging.exception("Unhandled error while processing update: %s", update)

    dispatcher.add_error_handler(error_handler)

    updater.start_polling(clean=True)
    updater.idle()


if __name__ == "__main__":
    main()


