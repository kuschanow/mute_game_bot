import re

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter, StateFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.dialogs.dialog_buttons import change_page, access_group as access_group_button, delete, update, create, change_name, group_access_settings
from bot.dialogs.dialog_menus import access_groups, access_group
from bot.dialogs.dialog_texts import access_settings_texts
from bot.filters import IsOwner, IsSuperAdmin
from bot.handlers.administrative.access_settings.access_group_creation_states import AccessGroupStates
from bot.handlers.administrative.access_settings.utils import select_settings_target
from bot.models import AccessGroup, Chat
from bot.utils import get_member_from_message
from shared.enums import SettingsTarget

group_access_settings_router = Router()
group_access_settings_router.callback_query.filter(DialogFilter("access_settings"), or_f(IsOwner(), IsSuperAdmin()))
group_access_settings_router.message.filter(or_f(IsOwner(), IsSuperAdmin()))


@group_access_settings_router.callback_query(ButtonFilter(create))
async def create_group(callback: CallbackQuery, dialog: Dialog, state: FSMContext):
    await dialog.set_state(state=AccessGroupStates.set_name, context=state)

    await dialog.edit_keyboard(callback.message.message_id, access_groups, menu_data={"creating": True})
    await callback.answer(_("Send name of new group"))


@group_access_settings_router.message(StateFilter(AccessGroupStates.set_name), F.content_type == ContentType.TEXT)
async def group_name(message: Message, dialog: Dialog, chat: Chat, state: FSMContext):
    name = message.text

    await message.delete()
    await dialog.remove_state(context=state)

    group: AccessGroup = await AccessGroup.objects.acreate(name=name, chat=chat)

    dialog.data["group_id"] = str(group.id)
    dialog.data["group_name"] = group.name

    await dialog.edit_message(dialog.values["main_message_id"], access_settings_texts["access_group"], access_group)


@group_access_settings_router.callback_query(ButtonFilter(change_name))
async def change_name(callback: CallbackQuery, dialog: Dialog, state: FSMContext):
    await dialog.set_state(state=AccessGroupStates.change_name, context=state)

    await dialog.edit_keyboard(callback.message.message_id, access_group, menu_data={"changing_name": True})
    await callback.answer(_("Send new name of group"))


@group_access_settings_router.message(StateFilter(AccessGroupStates.change_name), F.content_type == ContentType.TEXT)
async def change_name(message: Message, dialog: Dialog, state: FSMContext):
    name = message.text

    await message.delete()
    await dialog.remove_state(context=state)

    group: AccessGroup = await AccessGroup.objects.aget(id=dialog.data["group_id"])
    group.name = name
    dialog.data["group_name"] = name
    await group.asave()

    await dialog.edit_message(dialog.values["main_message_id"], access_settings_texts["access_group"], access_group)


@group_access_settings_router.callback_query(ButtonFilter(update, page="access_group"))
@group_access_settings_router.callback_query(ButtonFilter(access_group_button))
async def select_group(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)

    if "id" in button.data:
        dialog.data["group_id"] = button.data["id"]

    group: AccessGroup = await AccessGroup.objects.aget(id=dialog.data["group_id"])
    members = await sync_to_async(lambda: list(group.chatmember_set.all()))()

    dialog.data["group_name"] = group.name

    dialog.data["group_members"] = "\n".join([await sync_to_async(lambda: member.get_string())() for member in members])

    await dialog.edit_message(callback.message.message_id, access_settings_texts["access_group"], access_group)


@group_access_settings_router.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)

    dialog.data["page"] = button.data["page"]

    await dialog.edit_keyboard(callback.message.message_id, access_groups)


@group_access_settings_router.callback_query(ButtonFilter(delete))
async def delete_group(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    await (await AccessGroup.objects.aget(id=dialog.data["group_id"])).adelete()
    dialog.data.pop("group_id")

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_groups)


@group_access_settings_router.callback_query(ButtonFilter(group_access_settings))
async def change_settings(callback: CallbackQuery, chat: Chat, dialog: Dialog):
    await callback.answer()
    await select_settings_target(callback, chat, dialog, dialog.data["group_id"], SettingsTarget.GROUP.value, dialog.data["group_name"])


@group_access_settings_router.message(Command(settings.ADD_TO_GROUP_COMMAND))
async def add_to_group(message: Message):
    pattern = r"([0-9a-f]{8}(?:-?[0-9a-f]{4}){3}-?[0-9a-f]{12})(?: (\d+)| @(\w+))?$"
    match = re.search(pattern, message.text)

    if match:
        group_id, user_id, username = match.groups()

        member = await get_member_from_message(message, user_id, username)
    else:
        raise ValueError("Message text does not match the expected format.")

    member.access_group_id = group_id
    await member.asave()

    await message.answer(_("%(member)s added successfully") % {"member": await sync_to_async(lambda: member.get_string())()})
    await message.delete()


@group_access_settings_router.message(Command(settings.REMOVE_FROM_GROUP_COMMAND))
async def delete_from_group(message: Message):
    pattern = r"(\d+)| @(\w+)?$"
    match = re.search(pattern, message.text)

    if match:
        user_id, username = match.groups()

        member = await get_member_from_message(message, user_id, username)
    else:
        raise ValueError("Message text does not match the expected format.")

    member.access_group_id = None
    await member.asave()

    await message.answer(_("%(member)s deleted successfully") % {"member": await sync_to_async(lambda: member.get_string())()})
    await message.delete()
