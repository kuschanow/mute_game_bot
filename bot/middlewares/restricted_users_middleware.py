from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import CallbackQuery, ChatMemberRestricted


def set_restricted_user_middlewares(router: Router):
    router.callback_query.outer_middleware.register(callback_restricted_user_middleware)

async def callback_restricted_user_middleware(
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        callback: CallbackQuery,
        data: Dict[str, Any]
) -> Any:
    tele_member = await callback.chat.get_member(callback.from_user.id)
    if isinstance(tele_member, ChatMemberRestricted):
        if not tele_member.can_send_messages:
            return
    return await handler(callback, data)

