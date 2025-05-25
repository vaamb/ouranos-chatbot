from cachetools import TTLCache
from sqlalchemy.ext.asyncio import AsyncSession

from ouranos.core.database.models.app import anonymous_user, User, UserMixin


cache_users = TTLCache(maxsize=32, ttl=60)


async def get_current_user(session: AsyncSession, telegram_id: int) -> UserMixin:
    try:
        return cache_users[telegram_id]
    except KeyError:
        user = await User.get_by(session, telegram_id=telegram_id)
        if user:
            cache_users[telegram_id] = user
            session.expunge(user)
            session.expunge(user.role)
            return user
        return anonymous_user


async def link_user(
        session: AsyncSession,
        user: UserMixin,
        telegram_id: int,
) -> None:
    await User.update(session, user_id=user.id, values={"telegram_id": telegram_id})
