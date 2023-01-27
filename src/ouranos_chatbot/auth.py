import typing as t

from ouranos.core.database.models import anonymous_user, UserMixin
from ouranos.sdk import api


if t.TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_current_user(session: "AsyncSession", telegram_id: int) -> UserMixin:
    user = await api.user.get_by_telegram_id(session, telegram_id)
    if user:
        return user
    return anonymous_user


async def activate_user(
        session: "AsyncSession",
        user: UserMixin,
        telegram_id: int
) -> None:
    await api.user.update(session, user.id, {"telegram_chat_id": telegram_id})
