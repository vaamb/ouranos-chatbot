from telegram.ext import Application

from gaia_validators import missing
from ouranos.core.config import ConfigDict
from ouranos.sdk import Functionality

from ouranos_chatbot.config import Config


class Chatbot(Functionality):
    def __init__(self, config: ConfigDict, **kwargs) -> None:
        super().__init__(config, **kwargs)
        token = self.config.get("TELEGRAM_BOT_TOKEN", missing)
        if token is missing:
            self.logger.warning(
                "The config class used for Ouranos does not subclass "
                "`ouranos_chatbot.Config`. Falling back to default values.")
            token = Config().TELEGRAM_BOT_TOKEN
        if token is None:
            self.logger.error(
                "The config parameters 'TELEGRAM_BOT_TOKEN' is not set, it is "
                "not possible to use the chatbot functionality.")
        self.token = token
        self._application: Application | None = None

    @property
    def application(self) -> Application:
        if self._application is None:
            raise AttributeError(
                "The application has not been initialized. Run "
                "`build_application()` to initialize it.`"

            )
        return self._application

    def build_application(self) -> None:
        self._application = Application.builder().token(self.token).build()

    def load_handlers(self):
        from ouranos_chatbot.commands import HANDLERS

        for handler in HANDLERS:
            self.application.add_handler(handler)

    async def startup(self):
        if self.token is None:
            raise ValueError(
                "The config parameters 'TELEGRAM_BOT_TOKEN' is not set, it is "
                "not possible to use the chatbot functionality."
            )
        self.build_application()
        self.load_handlers()
        await self.application.initialize()
        # `Application`'s updater is automatically created with the default builder
        assert self.application.updater is not None
        await self.application.updater.start_polling()
        await self.application.start()

    async def shutdown(self):
        # `Application`'s updater is automatically created with the default builder
        assert self.application.updater is not None
        if self.application.updater.running:
            await self.application.updater.stop()
        if self.application.running:
            await self.application.stop()
        await self.application.shutdown()
