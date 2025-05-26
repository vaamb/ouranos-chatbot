from inspect import getdoc
from statistics import mean
from typing import Sequence

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, filters, MessageHandler

from dispatcher import AsyncDispatcher
import gaia_validators as gv
from ouranos import db
from ouranos.core.database.models.app import Permission, User
from ouranos.core.database.models.gaia import (
    ActuatorState, Ecosystem, Measure, SensorDataCache)
from ouranos.core.dispatchers import DispatcherFactory, DispatcherOptions
from ouranos.core.utils import Tokenizer, ExpiredTokenError, InvalidTokenError

from ouranos_chatbot.auth import link_user, get_current_user
from ouranos_chatbot.decorators import (
    activation_required, make_handler, permission_required)
from ouranos_chatbot.messages.templates import render_template


TELEGRAM_CHAT_ACTIVATION_SUB = "link_telegram"


DispatcherOptions.set_uri_lookup(
    "chatbot", DispatcherOptions.get_uri_lookup("application-internal"))
DispatcherOptions.set_options(
    "chatbot", DispatcherOptions.get_options("application-internal"))


async def _get_ecosystems(session, ecosystems: list[str] | None) -> Sequence[Ecosystem]:
    if ecosystems:
        return await Ecosystem.get_multiple(session, name=ecosystems)
    return await Ecosystem.get_multiple_by_id(session, ecosystems_id=["recent"])


def _summarize_sensors_data(sensors_data: list[SensorDataCache]) -> list[dict]:
    rv = {}
    for sensor_data in sensors_data:
        try:
            rv[sensor_data.measure].append(sensor_data.value)
        except KeyError:
            rv[sensor_data.measure] = [sensor_data.value]
    return [
        {
            "name": measure,
            "value": round(mean(data), 2),
        }
        for measure, data in rv.items()
    ]


def _summarize_actuators_state(actuators_state: list[ActuatorState]) -> list[dict]:
    return [
        {
            "name": actuator_state.type.name,
            "active": actuator_state.active,
            "mode": actuator_state.mode.name,
            "status": actuator_state.status,
        }
        for actuator_state in actuators_state
    ]


@make_handler(CommandHandler, "start")
async def start(update: Update, context: CallbackContext) -> None:
    """Start command."""
    telegram_id = update.effective_user.id
    async with db.scoped_session() as session:
        user = await get_current_user(session, telegram_id)
    if user.is_authenticated:
        greetings = f"Hi {user.firstname}"
    else:
        greetings = "Hello"
    await update.message.reply_html(
        f"{greetings}, welcome to GAIA! To see the commands available, "
        f"type /help."
    )


@make_handler(CommandHandler, "link_account")
async def link_account(update: Update, context: CallbackContext) -> None:
    """Link your account using the token received on the website or by email. Once
    linked, you will have access to more commands."""
    telegram_id = update.effective_user.id
    args = context.args
    if len(args) != 1:
        await update.message.reply_html(
            "You need to provide your activation token after the command"
        )
    token = args[0]
    try:
        payload = Tokenizer.loads(token)
        if payload["sub"] != TELEGRAM_CHAT_ACTIVATION_SUB:
            raise InvalidTokenError
        user_id: int = payload["user_id"]
        async with db.scoped_session() as session:
            user = await User.get(session, user_id=user_id)
            if not user:
                await update.message.reply_html(
                    "Could not find any user linked to this token"
                )
                return
            await link_user(session, user, telegram_id)
            await update.message.reply_html(
                f"Hi {user.username}. You are now allowed to fully use the "
                f"chatbot. To see the commands available, type /help"
            )
    except ExpiredTokenError:
        await update.message.reply_html(
            "This token has expired, ask for a new one and repeat the "
            "activation process"
        )
    except (InvalidTokenError, KeyError):
        await update.message.reply_html("This token is invalid")


@make_handler(CommandHandler, "ecosystems")
@activation_required
async def get_ecosystems(update: Update, context: CallbackContext) -> None:
    """Get the name of the ecosystems available."""
    async with db.scoped_session() as session:
        ecosystems = await Ecosystem.get_multiple_by_id(session, ecosystems_id=["recent"])
        msg = await render_template("ecosystems_available", ecosystems=ecosystems)
    await update.message.reply_html(msg)


@make_handler(CommandHandler, "ecosystems_status")
@activation_required
async def get_ecosystems_status(update: Update, context: CallbackContext) -> None:
    """Get the status of the ecosystem(s) specified or all if not specified."""
    ecosystems_name = context.args or None
    async with db.scoped_session() as session:
        ecosystems = await _get_ecosystems(session, ecosystems_name)
        msg = await render_template("ecosystems_status", ecosystems=ecosystems)
    await update.message.reply_html(msg)


@make_handler(CommandHandler, "sensors")
@activation_required
async def get_current_sensors(update: Update, context: CallbackContext) -> None:
    """Get the sensors measures from the ecosystem(s) specified or all if not
    specified."""
    ecosystems_name = context.args or None
    async with db.scoped_session() as session:
        ecosystems = await _get_ecosystems(session, ecosystems_name)
        data = [
            {
                "name": ecosystem.name,
                "current_data": _summarize_sensors_data(
                        await ecosystem.get_current_data(session)),
            }
            for ecosystem in ecosystems
        ]
        data = [ecosystem for ecosystem in data if ecosystem["current_data"]]
        measures = await Measure.get_multiple(session)
        units = {measure.name: measure.unit for measure in measures}
        msg = await render_template(
            "current_sensors", ecosystems=data, units=units)
    await update.message.reply_html(msg)


@make_handler(CommandHandler, "actuators_state")
@activation_required
async def get_actuators_state(update: Update, context: CallbackContext) -> None:
    """Get the actuators state from the ecosystem(s) specified or all if not
    specified."""
    ecosystems_name = context.args or None
    async with db.scoped_session() as session:
        ecosystems = await _get_ecosystems(session, ecosystems_name)
        data = [
            {
                "name": ecosystem.name,
                "actuators_state": _summarize_actuators_state(
                    await ecosystem.get_actuators_state(session)),
            }
            for ecosystem in ecosystems
        ]
        data = [ecosystem for ecosystem in data if ecosystem["actuators_state"]]
        msg = await render_template("actuators_state", ecosystems=data)
    await update.message.reply_html(msg)


@make_handler(CommandHandler, "switch_actuator")
@activation_required
@permission_required(Permission.OPERATE)
async def switch_actuator(update: Update, context: CallbackContext) -> None:
    """Switch an actuator on or off. Require to be an operator."""
    args = context.args
    if len(args) < 3 or len(args) > 4:
        await update.message.reply_text(
            "You need to provide the ecosystem, the actuator, the mode and "
            "optionally a countdown (in seconds)"
        )
        return
    ecosystem_name = args[0]
    # Get and sanitize actuator input
    actuator = args[1]
    try:
        actuator = gv.safe_enum_from_name(gv.HardwareType, actuator)
        if actuator not in gv.HardwareType.actuator:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            f"Actuator '{actuator}' is not a valid actuator. valid actuators are"
            f"{', '.join([x.name for x in gv.HardwareType.actuator])}")
        return
    actuator: gv.HardwareType
    # Get and sanitize mode input
    mode = args[2]
    try:
        mode = gv.safe_enum_from_name(gv.ActuatorModePayload, mode)
    except ValueError:
        await update.message.reply_text("Mode has to be 'on', 'off' or 'automatic'.")
        return
    mode: gv.ActuatorModePayload
    # Get and sanitize countdown input
    countdown: float = args[3] if len(args) == 4 else 0.0
    # Process to logic
    async with db.scoped_session() as session:
        ecosystem = await Ecosystem.get(session, name=ecosystem_name)
        if ecosystem is None:
            await update.message.reply_text(
                f"No ecosystem named '{ecosystem_name}' was found.")
            return
        actuator_state = await ecosystem.get_actuator_state(session, actuator)
        if not actuator_state.active:
            await update.message.reply_text(
                f"Ecosystem {ecosystem_name} is cannot manage {actuator.name}.")
            return
        dispatcher: AsyncDispatcher = DispatcherFactory.get("chatbot")
        await ecosystem.turn_actuator(dispatcher, actuator, mode, countdown)
        await update.message.reply_text(
            f"A request to turn {actuator.name} to {mode.name} has been sent to "
            f"{ecosystem_name}."
        )


def _get_command_helper(handler: CommandHandler) -> str:
    commands: list[str] = [i for i in handler.commands]
    if len(commands) > 1:
        raise ValueError("Only one command is allowed per handler")
    doc = getdoc(handler.callback).replace("\n", " ")
    return f"/{commands[0]} : {doc}\n"


@make_handler(CommandHandler, "help")
async def get_help(update: Update, context: CallbackContext) -> None:
    telegram_id = update.effective_user.id
    async with db.scoped_session() as session:
        user = await get_current_user(session, telegram_id)
    msg = "Here is a list of the commands available:\n"
    if user.is_anonymous:
        msg += _get_command_helper(link_account)
        await update.message.reply_html(msg)
        return
    msg += _get_command_helper(get_ecosystems)
    msg += _get_command_helper(get_ecosystems_status)
    msg += _get_command_helper(get_current_sensors)
    msg += _get_command_helper(get_actuators_state)
    if user.can(Permission.OPERATE):
        msg += _get_command_helper(switch_actuator)
    await update.message.reply_text(msg)


@make_handler(MessageHandler, filters.COMMAND)
async def unknown_command(update: Update, context: CallbackContext):
    telegram_id = update.effective_user.id
    async with db.scoped_session() as session:
        user = await get_current_user(session, telegram_id)
    if user.is_authenticated:
        sorry = f"Sorry {user.username},"
    else:
        sorry = "Sorry,"
    await update.message.reply_text(
        f"{sorry} I did not understand that command. Use /help to see the "
        f"commands available")


HANDLERS = [
    start,
    get_ecosystems,
    get_ecosystems_status,
    get_current_sensors,
    get_actuators_state,
    switch_actuator,
    get_help,
    unknown_command,
]
