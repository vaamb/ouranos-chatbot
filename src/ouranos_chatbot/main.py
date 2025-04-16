import typing as t

import click
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, filters, MessageHandler)

from gaia_validators import missing
from ouranos import current_app
from ouranos.sdk import Functionality, run_functionality_forever

from ouranos_chatbot.config import Config


if t.TYPE_CHECKING:
    from ouranos.core.config import profile_type


@click.command()
@click.option(
    "--config-profile",
    type=str,
    default=None,
    help="Configuration profile to use as defined in config.py.",
    show_default=True,
)
def main(
        config_profile: str,
) -> None:
    """Launch Ouranos'Chatbot

    The Chatbot provides a communication mean between Ouranos and the user
    using telegram. It provides commands that allows the user to get data from
    the database and manage Gaia's instances
    """
    run_functionality_forever(Chatbot, config_profile)


class Chatbot(Functionality):
    def __init__(
            self,
            config_profile: "profile_type" = None,
            config_override: dict | None = None,
            **kwargs
    ) -> None:
        super().__init__(config_profile, config_override, **kwargs)
        token = current_app.config.get("TELEGRAM_BOT_TOKEN", missing)
        if token is missing:
            self.logger.warning(
                "The config class used for Ouranos does not subclass "
                "`ouranos_chatbot.Config`. Falling back to default values."
            )
            token = Config().TELEGRAM_BOT_TOKEN
        if token is None:
            self.logger.error(
                "The config parameters 'TELEGRAM_BOT_TOKEN' is not set, it is"
                "not possible to use the chatbot functionality"
            )
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
