from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.dialogs.dialog_buttons import games_settings, can_join_games, can_create_games, can_press_other_buttons, can_create_punishments, \
    can_delete_punishments, settings_target as settings_target_button, make_diff, reset_to_global, show_in_stats, is_invulnerable
from bot.dialogs.dialog_menus import settings_target, access_settings, game_settings_select, access_groups
from bot.dialogs.dialog_texts import access_settings_texts
from bot.filters import IsOwner, IsSuperAdmin
from bot.generate_session import bot
from bot.handlers.administrative.access_settings.utils import select_settings_target
from bot.models import AccessSettings, Chat, AccessSettingsObject, ChatMember
from shared.enums import SettingsTarget

main_access_settings_router = Router()
main_access_settings_router.callback_query.filter(DialogFilter("access_settings"), or_f(IsOwner(), IsSuperAdmin()))
main_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), or_f(IsOwner(), IsSuperAdmin()))


@main_access_settings_router.message(Command(settings.ACCESS_SETTINGS_COMMAND))
async def access_settings_command(message: Message, member: ChatMember, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()

    dialog = Dialog.create("access_settings", user_id=member.user_id, chat_id=member.chat_id, bot=bot)

    dialog.data["is_super_admin"] = member.is_super_admin()

    bot_message = await dialog.send_message(access_settings_texts["target"], settings_target)
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)

    await message.delete()


@main_access_settings_router.callback_query(ButtonFilter(settings_target_button, target="super_admin"), IsSuperAdmin())
async def super_admin_settings(callback: CallbackQuery, member: ChatMember, chat: Chat, dialog: Dialog):
    await callback.answer()
    await select_settings_target(callback, chat, dialog, str(member.id), SettingsTarget.SUPER_ADMIN.value, _("Super admin"))


@main_access_settings_router.callback_query(ButtonFilter(settings_target_button, target="owner"))
async def owner_settings(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()
    await select_settings_target(callback, chat, dialog, str(chat.id), SettingsTarget.OWNER.value, _("Owner"))


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
    await select_settings_target(callback, chat, dialog, str(chat.id), SettingsTarget.ADMINS.value, _("Admins"))


@main_access_settings_router.callback_query(ButtonFilter(settings_target_button, target="group"))
async def group_selection(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    dialog.data["target"] = "group"
    dialog.data["target_name"] = _("Group")
    dialog.data["add_to_group_command"] = settings.ADD_TO_GROUP_COMMAND
    dialog.data["remove_from_group_command"] = settings.REMOVE_FROM_GROUP_COMMAND

    dialog.data["page"] = 0

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_groups)


@main_access_settings_router.callback_query(ButtonFilter(reset_to_global))
async def clear_settings(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.data["settings_object_id"])
    await settings_object.adelete()

    dialog.data["settings_object_id"] = None

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": None})


@main_access_settings_router.callback_query(ButtonFilter(make_diff))
async def make_diff(callback: CallbackQuery, chat: Chat, member: ChatMember, dialog: Dialog):
    await callback.answer()

    reference = await sync_to_async(
            lambda: AccessSettings.objects.get(chat=chat, target=SettingsTarget.CHAT.value, target_id=chat.id).settings_object)()
    target_id = None

    if dialog.data["target"] == SettingsTarget.SUPER_ADMIN.value:
        reference = await AccessSettingsObject.get_full_access_settings()
        target_id = member.id

    if dialog.data["target"] == SettingsTarget.ADMINS.value:
        target_id = chat.id

    if dialog.data["target"] == SettingsTarget.GROUP.value:
        target_id = dialog.data["group_id"]

    settings_object = reference
    settings_object.pk = None
    await settings_object.asave()

    await AccessSettings(chat=chat, target=dialog.data["target"], target_id=target_id, settings_object=settings_object).asave()

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
@main_access_settings_router.callback_query(ButtonFilter(is_invulnerable))
@main_access_settings_router.callback_query(ButtonFilter(show_in_stats))
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
