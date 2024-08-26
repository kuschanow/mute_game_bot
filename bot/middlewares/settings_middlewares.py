from typing import Callable, Dict, Any, Awaitable

from aiogram import Router
from aiogram.types import TelegramObject
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.models.AccessSettings import AccessSettings
from bot.models.AccessSettingsObject import AccessSettingsObject
from shared.enums import SettingsTarget, MemberStatus, InteractionLevel


def set_settings_middlewares(router: Router):
    router.message.outer_middleware.register(settings_middleware)
    router.callback_query.outer_middleware.register(settings_middleware)

async def settings_middleware(
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
) -> Any:
    if data["member"].is_owner():
        data["member_settings"] = await AccessSettingsObject.get_owner_settings()
        return await handler(event, data)

    if await AccessSettings.objects.filter(chat=data["chat"], target=SettingsTarget.MEMBER.value).aexists():
        _settings = await AccessSettings.objects.aget(chat=data["chat"], target=SettingsTarget.MEMBER.value, target_id=data["member"].id)
    elif data["member"].settings_group_id is not None:
        _settings = await AccessSettings.objects.aget(chat=data["chat"], target=SettingsTarget.GROUP.value, target_id=data["member"].settings_group_id)
    elif data["member"].is_admin() and await AccessSettings.objects.filter(chat=data["chat"], target=SettingsTarget.ADMINS.value).aexists():
            _settings = await AccessSettings.objects.aget(chat=data["chat"], target=SettingsTarget.ADMINS.value, target_id=data["chat"].id)
    else:
        _settings = await AccessSettings.objects.aget(chat=data["chat"], target=SettingsTarget.CHAT.value, target_id=data["chat"].id)

    data["member_settings"] = await sync_to_async(lambda: _settings.settings_object)()
    return await handler(event, data)


