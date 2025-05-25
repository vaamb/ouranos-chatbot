from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, filters, MessageHandler)

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
                "The config parameters 'TELEGRAM_BOT_TOKEN' is not set, it is"
                "not possible to use the chatbot functionality.")
        self.token = token
        self.application: Application | None = None

    def load_handlers(self):
        from ouranos_chatbot.commands import (
            ecosystem_status, help_cmd, start, unknown_command
        )
        start_handler = CommandHandler('start', start)
        self.application.add_handler(start_handler)

        ecosystem_status_handler = CommandHandler('ecosystem_status', ecosystem_status)
        self.application.add_handler(ecosystem_status_handler)

        help_handler = CommandHandler("help", help_cmd)
        self.application.add_handler(help_handler)

        unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
        self.application.add_handler(unknown_command_handler)

    async def _startup(self):
        if self.token is None:
            raise ValueError(
                "The config parameters 'TELEGRAM_BOT_TOKEN' is not set,"
                "it is not possible to use the chatbot functionality"
            )
        self.application = ApplicationBuilder().token(self.token).build()
        self.load_handlers()
        await self.application.initialize()
        await self.application.updater.start_polling()
        await self.application.start()

    async def _shutdown(self):
        if self.application.updater.running:
            await self.application.updater.stop()
        if self.application.running:
            await self.application.stop()
        await self.application.shutdown()
