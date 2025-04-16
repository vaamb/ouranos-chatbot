import os

class Config:
    TELEGRAM_BOT_TOKEN: str | None = os.environ.get("OURANOS_TELEGRAM_BOT_TOKEN", None)
