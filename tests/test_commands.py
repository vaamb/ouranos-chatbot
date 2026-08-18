from datetime import datetime, timedelta, timezone

import pytest

from ouranos.core.database.models.app import User
from ouranos.core.utils import Tokenizer

from ouranos_chatbot.commands import (
    TELEGRAM_CHAT_ACTIVATION_SUB, get_ecosystems, link_account)


async def _create_user(session, **overrides) -> User:
    values = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password1!",
    }
    values.update(overrides)
    await User.create(session, values=values)
    user = await User.get_by(session, username=values["username"])
    assert user is not None
    return user


@pytest.mark.asyncio
class TestLinkAccount:
    async def test_missing_token(self, make_update, make_context):
        update = make_update()
        context = make_context(args=[])

        await link_account.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "provide your activation token" in msg

    async def test_invalid_token(self, make_update, make_context):
        update = make_update()
        context = make_context(args=["not-a-real-token"])

        await link_account.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "This token is invalid" in msg

    async def test_wrong_subject(self, make_update, make_context):
        token = Tokenizer.dumps({"sub": "some_other_subject", "user_id": 1})
        update = make_update()
        context = make_context(args=[token])

        await link_account.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "This token is invalid" in msg

    async def test_expired_token(self, make_update, make_context):
        payload = {
            "sub": TELEGRAM_CHAT_ACTIVATION_SUB,
            "user_id": 1,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        token = Tokenizer.dumps(payload)
        update = make_update()
        context = make_context(args=[token])

        await link_account.callback(update, context)

        (msg,), _ = update.message.reply_html.call_args
        assert "expired" in msg

    async def test_unknown_user(self, make_update, make_context):
        token = Tokenizer.dumps(
            {"sub": TELEGRAM_CHAT_ACTIVATION_SUB, "user_id": 424242})
        update = make_update()
        context = make_context(args=[token])

        await link_account.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "Could not find any user linked to this token" in msg

    async def test_success_links_the_telegram_id(self, db, make_update, make_context):
        async with db.scoped_session() as session:
            user = await _create_user(session)
            user_id = user.id

        token = Tokenizer.dumps({
            "sub": TELEGRAM_CHAT_ACTIVATION_SUB,
            "user_id": user_id,
        })
        telegram_id = 987654
        update = make_update(telegram_id=telegram_id)
        context = make_context(args=[token])

        await link_account.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "You are now allowed" in msg

        async with db.scoped_session() as session:
            linked_user = await User.get_by(session, telegram_id=telegram_id)
            assert linked_user is not None
            assert linked_user.id == user_id


@pytest.mark.asyncio
class TestActivationRequired:
    """Exercises the `activation_required` decorator through `get_ecosystems`,
    a command that uses it."""

    async def test_rejects_an_unlinked_telegram_account(self, make_update, make_context):
        update = make_update(telegram_id=111111)
        context = make_context()

        await get_ecosystems.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert "You need to be registered to use this command" in msg

    async def test_lets_a_linked_account_through(self, db, make_update, make_context):
        telegram_id = 222222
        async with db.scoped_session() as session:
            await _create_user(session, telegram_id=telegram_id)

        update = make_update(telegram_id=telegram_id)
        context = make_context()

        await get_ecosystems.callback(update, context)

        update.message.reply_html.assert_awaited_once()
        (msg,), _ = update.message.reply_html.call_args
        assert msg == "There is not ecosystem currently registered to GAIA"
