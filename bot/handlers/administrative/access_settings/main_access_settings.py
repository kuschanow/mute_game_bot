import uuid
from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import IsOwner, DialogAccess
from bot.models import AccessSettings, Chat, AccessSettingsObject, ChatMember
from shared import target, redis
from shared.enums import SettingsTarget
from .utils.access_settings_keyboards import get_settings_targets_keyboard, get_settings_keyboard, get_games_select_keyboard

main_access_settings_router = Router()
main_access_settings_router.callback_query.filter(F.data.startswith("stgs"), IsOwner(), DialogAccess())
main_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), IsOwner())


@main_access_settings_router.message(Command(settings.ACCESS_SETTINGS_COMMAND))
async def access_settings_command(message: Message, member: ChatMember):
    settings_message = await message.answer(text=_("Select target"), reply_markup=get_settings_targets_keyboard())

    data = await redis.get_deserialized(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {}

    data["dialogs"][str(settings_message.message_id)] = {"date": str(datetime.utcnow())}
    await redis.set_serialized(str(member.id), data)

    await message.delete()


@main_access_settings_router.callback_query(F.data.contains("targets:chat"))
async def chat_settings(callback: CallbackQuery, chat: Chat, member: ChatMember):
    _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
    settings_object = await sync_to_async(lambda: _settings.settings_object)()

    data = await redis.get_deserialized(str(member.id))

    await callback.message.edit_text(text=target["chat"],
                                     reply_markup=get_settings_keyboard(settings_object, "chat"))

    data["dialogs"][str(callback.message.message_id)]["settings_object_id"] = str(settings_object.id)
    await redis.set_serialized(str(member.id), data)

    await callback.answer()


@main_access_settings_router.callback_query(F.data.contains("targets:admins"))
async def admins_settings(callback: CallbackQuery, chat: Chat, member: ChatMember):
    if not await AccessSettings.objects.filter(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id).aexists():
        settings_object_for_admins = None
    else:
        _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        settings_object_for_admins = await sync_to_async(lambda: _settings.settings_object)()

    data = await redis.get_deserialized(str(member.id))

    await callback.message.edit_text(text=target["admins"],
                                     reply_markup=get_settings_keyboard(settings_object_for_admins, "admins"))

    data["dialogs"][str(callback.message.message_id)]["settings_object_id"] = str(settings_object_for_admins.id)
    await redis.set_serialized(str(member.id), data)

    await callback.answer()


@main_access_settings_router.callback_query(F.data == "stgs:targets")
async def settings_targets(callback: CallbackQuery):
    await callback.message.edit_text(text=_("Select target"), reply_markup=get_settings_targets_keyboard())
    await callback.answer()


@main_access_settings_router.callback_query(F.data.endswith("clear"))
async def clear_settings(callback: CallbackQuery, chat: Chat, member: ChatMember):
    target_id = callback.data.split(":")[1]

    if target_id == "admins":
        _settings: AccessSettings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        await (await sync_to_async(lambda: _settings.settings_object)()).adelete()

    data = await redis.get_deserialized(str(member.id))
    data["dialogs"][str(callback.message.message_id)]["settings_object_id"] = None
    await redis.set_serialized(str(member.id), data)

    await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(None, "admins"))
    await callback.answer()


@main_access_settings_router.callback_query(F.data.endswith("make_diff"))
async def make_diff(callback: CallbackQuery, chat: Chat, member: ChatMember):
    target_id = callback.data.split(":")[1]

    settings_object_for_admins = None

    if target_id == "admins":
        _chat_settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
        settings_object_for_chat: AccessSettingsObject = await sync_to_async(lambda: _chat_settings.settings_object)()
        settings_object_for_admins = settings_object_for_chat
        settings_object_for_admins.pk = None
        await settings_object_for_admins.asave()

        await AccessSettings(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id, settings_object=settings_object_for_admins).asave()

    data = await redis.get_deserialized(str(member.id))
    data["dialogs"][str(callback.message.message_id)]["settings_object_id"] = str(settings_object_for_admins.id) if settings_object_for_admins else None
    await redis.set_serialized(str(member.id), data)

    await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(settings_object_for_admins, target_id))
    await callback.answer()


@main_access_settings_router.callback_query(F.data.contains("set"))
async def main_settings(callback: CallbackQuery, member: ChatMember):
    data = await redis.get_deserialized(str(member.id))
    settings_object_id = uuid.UUID(data["dialogs"][str(callback.message.message_id)]["settings_object_id"])
    parameter = callback.data.split(":")[-2]
    target_id = callback.data.split(":")[1]

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=settings_object_id)

    if parameter == "join_games":
        settings_object.can_join_games = not settings_object.can_join_games
    if parameter == "create_games":
        settings_object.can_create_games = not settings_object.can_create_games
    if parameter == "press_other_buttons":
        settings_object.can_press_other_buttons = not settings_object.can_press_other_buttons
    if parameter == "create_punishments":
        settings_object.can_create_public_punishments = not settings_object.can_create_public_punishments
    if parameter == "delete_punishments":
        settings_object.can_delete_public_punishments = not settings_object.can_delete_public_punishments

    await settings_object.asave()

    try:
        await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(settings_object, target_id))
    except:
        pass
    await callback.answer()


@main_access_settings_router.callback_query(F.data.contains("games_menu"))
async def games_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    target_id = callback.data.split(":")[1]

    try:
        await callback.message.edit_text(text=_("Select game"), reply_markup=get_games_select_keyboard(target_id))
    except:
        pass
    await callback.answer()
