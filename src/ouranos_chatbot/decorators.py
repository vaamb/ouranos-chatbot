import functools
from inspect import signature
from typing import Type

from telegram import Update
from telegram.ext import BaseHandler, CallbackContext
from telegram.ext.filters import BaseFilter

from ouranos import db
from ouranos.core.database.models.app import Permission, User

from ouranos_chatbot.auth import get_current_user


def make_handler(handler: Type[BaseHandler], command_or_filter: str | BaseFilter):
    def decorator(func):
        return handler(command_or_filter, func)
    return decorator


def activation_required(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: CallbackContext):
        telegram_id = update.effective_user.id
        async with db.scoped_session() as session:
            user = await get_current_user(session, telegram_id)
        if user.is_anonymous:
            await update.message.reply_html(
                "You need to be registered to use this command")
            return
        if "user" in signature(func).parameters:
            return await func(update, context, user)
        return await func(update, context)
    return wrapper


def permission_required(permission: Permission):
    def decorator(func):
        @functools.wraps(func)
        async def wrapped(
                update: Update,
                context: CallbackContext,
                user: User | None = None
        ):
            if not user:
                telegram_id = update.effective_user.id
                async with db.scoped_session() as session:
                    user = await get_current_user(session, telegram_id)
            if user.can(permission):
                if "user" in signature(func).parameters:
                    return await func(update, context, user)
                return await func(update, context)
            else:
                await update.message.reply_html(
                    "You do not have the permission to use this command"
                )
        return wrapped
    return decorator
