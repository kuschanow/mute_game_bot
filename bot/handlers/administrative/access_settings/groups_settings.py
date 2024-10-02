import re

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.dialogs.dialog_buttons import change_page, access_group as access_group_button, delete, update
from bot.dialogs.dialog_menus import access_groups, access_group
from bot.dialogs.dialog_texts import access_settings_texts
from bot.filters import IsOwner
from bot.models import AccessGroup, ChatMember
from bot.utils import get_member_from_message

group_access_settings = Router()
group_access_settings.callback_query.filter(DialogFilter("access_settings"), IsOwner())
group_access_settings.message.filter(IsOwner())


@group_access_settings.callback_query(ButtonFilter(update, page="access_group"))
@group_access_settings.callback_query(ButtonFilter(access_group_button))
async def select_group(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance):
    await callback.answer()

    dialog.data["group_name"] = button.data["name"]
    dialog.data["group_id"] = button.data["id"]

    group: AccessGroup = await AccessGroup.objects.aget(id=dialog.data["group_id"])
    members = await sync_to_async(lambda: group.chatmember_set)()

    dialog.data["group_members"] = "\n".join([member.get_string() for member in members])
    dialog.data["add_to_group_command"] = settings.ADD_TO_GROUP_COMMAND

    await dialog.edit_message(callback.message.message_id, access_settings_texts["access_group"], access_group)


@group_access_settings.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance):
    await callback.answer()
    dialog.data["page"] = button.data["page"]

    await dialog.edit_keyboard(callback.message.message_id, access_groups)


@group_access_settings.callback_query(ButtonFilter(delete))
async def delete_group(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    await (await AccessGroup.objects.aget(id=dialog.data["group_id"])).adelete()
    dialog.data.pop("group_id")

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_groups)


@group_access_settings.message(Command(settings.ADD_TO_GROUP_COMMAND))
async def add_to_group(message: Message):
    pattern = r"([0-9a-f]{8}(?:-?[0-9a-f]{4}){3}-?[0-9a-f]{12})(?: (\d+)| @(\w+))?$"
    match = re.match(pattern, message.text)

    if match:
        group_id, user_id, username = match.groups()

        member = await get_member_from_message(message, user_id, username)
    else:
        raise ValueError("Message text does not match the expected format.")

    member.access_group_id = group_id
    await member.asave()

    await message.answer(_("Added successfully"))


@group_access_settings.message(Command(settings.DELETE_FROM_GROUP_COMMAND))
async def delete_from_group(message: Message):
    pattern = r"(\d+)| @(\w+)?$"
    match = re.match(pattern, message.text)

    if match:
        user_id, username = match.groups()

        member = await get_member_from_message(message, user_id, username)
    else:
        raise ValueError("Message text does not match the expected format.")

    member.access_group_id = None
    await member.asave()

    await message.answer(_("Deleted successfully"))

