from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import IsOwner
from bot.generate_session import bot
from bot.models import AccessSettings, Chat, AccessSettingsObject, ChatMember
from bot.utils.dialog.dialog_buttons import games_settings, can_join_games, can_create_games, can_press_other_buttons, can_create_punishments, \
    can_delete_punishments
from bot.utils.dialog.dialog_buttons import settings_target as settings_target_button, make_diff, reset_to_global
from bot.utils.dialog.dialog_menus import settings_target, access_settings, game_settings_select
from bot.utils.dialog.dialog_texts import access_settings_texts
from shared.enums import SettingsTarget

main_access_settings_router = Router()
main_access_settings_router.callback_query.filter(DialogFilter("access_settings"), IsOwner())
main_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), IsOwner())


@main_access_settings_router.message(Command(settings.ACCESS_SETTINGS_COMMAND))
async def access_settings_command(message: Message, member: ChatMember, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()

    dialog = Dialog.create("access_settings", user_id=member.user_id, chat_id=member.chat_id, bot=bot)

    bot_message = await dialog.send_message(access_settings_texts["target"], settings_target)
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)

    await message.delete()


@main_access_settings_router.callback_query(ButtonFilter(settings_target_button, target="chat"))
async def chat_settings(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()

    _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
    settings_object = await sync_to_async(lambda: _settings.settings_object)()

    dialog.data["target"] = "chat"
    dialog.data["target_name"] = _("Global")

    dialog.data["settings_object_id"] = str(settings_object.id)

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": settings_object})


@main_access_settings_router.callback_query(ButtonFilter(settings_target_button, target="admins"))
async def admins_settings(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()

    if not await AccessSettings.objects.filter(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id).aexists():
        settings_object_for_admins = None
    else:
        _settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        settings_object_for_admins = await sync_to_async(lambda: _settings.settings_object)()

    dialog.data["target"] = "admins"
    dialog.data["target_name"] = _("Admins")

    dialog.data["settings_object_id"] = str(settings_object_for_admins.id)

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": settings_object_for_admins})


@main_access_settings_router.callback_query(ButtonFilter(reset_to_global))
async def clear_settings(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()

    if dialog.data["target"] == "admins":
        _settings: AccessSettings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id)
        await (await sync_to_async(lambda: _settings.settings_object)()).adelete()

    dialog.data["settings_object_id"] = None

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": None})


@main_access_settings_router.callback_query(ButtonFilter(make_diff))
async def make_diff(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()

    settings_object = None

    if dialog.data["target"] == "admins":
        _chat_settings = await AccessSettings.objects.aget(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id)
        settings_object_for_chat: AccessSettingsObject = await sync_to_async(lambda: _chat_settings.settings_object)()
        settings_object = settings_object_for_chat
        settings_object.pk = None
        await settings_object.asave()

        await AccessSettings(chat=chat, target=SettingsTarget.ADMINS.value, target_id=chat.id, settings_object=settings_object).asave()

    dialog.data["settings_object_id"] = str(settings_object.id)

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": settings_object})


@main_access_settings_router.callback_query(ButtonFilter(can_join_games))
@main_access_settings_router.callback_query(ButtonFilter(can_create_games))
@main_access_settings_router.callback_query(ButtonFilter(can_press_other_buttons))
@main_access_settings_router.callback_query(ButtonFilter(can_create_punishments))
@main_access_settings_router.callback_query(ButtonFilter(can_delete_punishments))
async def main_settings(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance):
    await callback.answer()

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.values["settings_object_id"])

    current_value = getattr(settings_object, button.type_name)
    setattr(settings_object, button.type_name, not current_value)

    await settings_object.asave()

    await dialog.edit_keyboard(
        callback.message.message_id,
        access_settings,
        menu_data={"settings_object": settings_object}
    )


@main_access_settings_router.callback_query(ButtonFilter(games_settings))
async def games_menu(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    await dialog.edit_message(callback.message.message_id, access_settings_texts["base_settings"], game_settings_select)
