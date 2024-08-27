import uuid

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import IsOwner
from shared.enums import SettingsTarget
from .utils.chat_settings_keyboards import get_settings_targets_keyboard, get_settings_keyboard
from bot.models import AccessSettings, Chat, AccessSettingsObject

main_access_settings_router = Router()
main_access_settings_router.callback_query.filter(F.data.startswith("stgs"), IsOwner())
main_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), IsOwner())


@main_access_settings_router.message(Command(settings.ACCESS_SETTINGS_COMMAND))
async def access_settings_command(message: Message):
    await message.answer(text=_("Select target"), reply_markup=get_settings_targets_keyboard())
    await message.delete()


@main_access_settings_router.callback_query(F.data.contains("targets:chat"))
async def chat_settings(callback: CallbackQuery, chat: Chat):
    _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
    settings_object = await sync_to_async(lambda: _settings.settings_object)()

    await callback.message.edit_text(text=_("Global settings"),
                                     reply_markup=get_settings_keyboard(settings_object, 0))
    await callback.answer()


@main_access_settings_router.callback_query(F.data.contains("targets:admins"))
async def admins_settings(callback: CallbackQuery, chat: Chat):
    if not await AccessSettings.objects.filter(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id).aexists():
        settings_object_for_admins = None
    else:
        _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        settings_object_for_admins = await sync_to_async(lambda: _settings.settings_object)()

    await callback.message.edit_text(text=_("Admins settings"),
                                     reply_markup=get_settings_keyboard(settings_object_for_admins, 1))
    await callback.answer()


@main_access_settings_router.callback_query(F.data == "stgs:targets")
async def settings_targets(callback: CallbackQuery):
    await callback.message.edit_text(text=_("Select target"), reply_markup=get_settings_targets_keyboard())
    await callback.answer()


@main_access_settings_router.callback_query(F.data.endswith("clear"))
async def clear_settings(callback: CallbackQuery, chat: Chat):
    _type = int(callback.data.split(":")[1])

    if _type == 1:
        _settings: AccessSettings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        await (await sync_to_async(lambda: _settings.settings_object)()).adelete()

    await callback.message.edit_text(text=callback.message.text, reply_markup=get_settings_keyboard(None, 1))
    await callback.answer()


@main_access_settings_router.callback_query(F.data.endswith("make_diff"))
async def make_diff(callback: CallbackQuery, chat: Chat):
    _type = int(callback.data.split(":")[1])

    settings_object_for_admins = None

    if _type == 1:
        _chat_settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
        settings_object_for_chat: AccessSettingsObject = await sync_to_async(lambda: _chat_settings.settings_object)()
        settings_object_for_admins = settings_object_for_chat
        settings_object_for_admins.pk = None
        await settings_object_for_admins.asave()

        await AccessSettings(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id, settings_object=settings_object_for_admins).asave()

    await callback.message.edit_text(text=callback.message.text, reply_markup=get_settings_keyboard(settings_object_for_admins, _type))
    await callback.answer()


@main_access_settings_router.callback_query(F.not_contains("games_menu"), F.data.contains("-"))
async def main_settings(callback: CallbackQuery):
    settings_object_id = uuid.UUID(callback.data.split(":")[-1])
    parameter = callback.data.split(":")[-2]
    _type = int(callback.data.split(":")[1])

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
        await callback.message.edit_text(text=callback.message.text, reply_markup=get_settings_keyboard(settings_object, _type))
    except:
        pass
    await callback.answer()
