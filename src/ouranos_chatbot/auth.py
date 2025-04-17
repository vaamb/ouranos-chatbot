from sqlalchemy.ext.asyncio import AsyncSession

from ouranos.core.database.models.app import anonymous_user, User, UserMixin


async def get_current_user(session: AsyncSession, telegram_id: int) -> UserMixin:
    user = await User.get_by(session, telegram_id=telegram_id)
    if user:
        return user
    return anonymous_user


async def link_user(
        session: AsyncSession,
        user: UserMixin,
        telegram_id: int,
) -> None:
    await User.update(session, user_id=user.id, values={"telegram_id": telegram_id})
