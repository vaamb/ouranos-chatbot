import asyncio
from asyncio import sleep

import pytest
from telegram.ext import Application, ExtBot

from ouranos.core.plugins_manager import PluginManager

from ouranos_chatbot.main import Chatbot


class FakeBot(ExtBot):
    """An `ExtBot` that never touches the network."""
    async def _do_post(self, endpoint: str, data: dict, **kwargs):
        if endpoint == "getMe":
            return {
                "id": 123456789,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "test_bot",
            }
        if endpoint == "getUpdates":
            # Avoid busy-looping the polling task.
            await asyncio.sleep(0.05)
            return []
        if endpoint in ("deleteWebhook", "close", "logOut"):
            return True
        raise NotImplementedError(f"FakeBot does not support endpoint {endpoint!r}")


@pytest.fixture()
def patch_build_application(monkeypatch):
    def fake_build_application(self: Chatbot) -> None:
        fake_bot = FakeBot(token=self.token)
        self._application = Application.builder().bot(fake_bot).build()

    monkeypatch.setattr(Chatbot, "build_application", fake_build_application)


@pytest.mark.asyncio
class TestPlugin:
    async def test_plugin_lifecycle(self, config, patch_build_application):
        # The config fixture is used to set up the config globally
        pm = PluginManager()
        pm.register_plugins()

        chatbot = pm.load_plugin("chatbot")
        chatbot.compute_number_of_workers = lambda: 0

        chatbot.setup_config(config)

        await chatbot.startup()

        await sleep(0.2)
        assert chatbot.is_started

        await chatbot.shutdown()

        await sleep(0.2)
        assert not chatbot.is_started
