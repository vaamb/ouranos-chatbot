from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from ouranos import Config, db as _db, setup_config
from ouranos.core.config import ConfigDict
from ouranos.core.database.init import create_db_tables, insert_default_data


@pytest.fixture(scope="session", autouse=True)
def config(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("base-dir")

    Config.DIR = str(tmp_path)
    Config.TESTING = True
    Config.SQLALCHEMY_DATABASE_URI = "sqlite+aiosqlite://"
    Config.SQLALCHEMY_BINDS = {
        "app": "sqlite+aiosqlite://",
        "system": "sqlite+aiosqlite://",
        "archive": "sqlite+aiosqlite://",
        "transient": "sqlite+aiosqlite://",
    }
    Config.TELEGRAM_BOT_TOKEN = "DefAToken"

    config = setup_config(Config)
    _db.init(config)
    yield config


@pytest_asyncio.fixture(autouse=True)
async def db(config: ConfigDict):
    from ouranos.core.database.models import app, archives, caches, gaia, system  # noqa: F401

    await create_db_tables()
    await insert_default_data()

    yield _db

    await _db.drop_all()

    for key, value in caches.__dict__.items():
        if key.startswith("cache_"):
            value.clear()


@pytest.fixture
def make_update():
    """Build a minimal fake `telegram.Update` for a command callback."""
    def _make_update(telegram_id: int = 123456) -> MagicMock:
        update = MagicMock()
        update.effective_user.id = telegram_id
        update.message.reply_html = AsyncMock()
        update.message.reply_text = AsyncMock()
        return update
    return _make_update


@pytest.fixture
def make_context():
    """Build a minimal fake `telegram.ext.CallbackContext` for a command callback."""
    def _make_context(args: list[str] | None = None) -> MagicMock:
        context = MagicMock()
        context.args = args or []
        return context
    return _make_context
