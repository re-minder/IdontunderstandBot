import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    # dotenv is optional at runtime; safe to ignore if missing on server
    pass


@dataclass(frozen=True)
class BotConfig:
    bot_token: str
    owner_id: int
    database_path: str


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name, default)
    return value


def load_config() -> BotConfig:
    bot_token = get_env("BOT_TOKEN")
    owner_id_str = get_env("BOT_OWNER_ID")
    database_path = get_env("BOT_DB_PATH", os.path.join(os.getcwd(), "data", "bot.db"))

    if not bot_token:
        raise RuntimeError("BOT_TOKEN environment variable is required")
    if not owner_id_str:
        raise RuntimeError("BOT_OWNER_ID environment variable is required (Telegram numeric user id)")

    try:
        owner_id = int(owner_id_str)
    except ValueError as exc:
        raise RuntimeError("BOT_OWNER_ID must be an integer") from exc

    return BotConfig(
        bot_token=bot_token,
        owner_id=owner_id,
        database_path=database_path,
    )


