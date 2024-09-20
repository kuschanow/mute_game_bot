import re
from datetime import timedelta

from aiogram import Router, F
from aiogram.enums import ChatType, ContentType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import StateFilter, ButtonFilter, DialogFilter, DialogAccessFilter
from aiogram_dialog_manager.instance import Dialog, ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import User, Chat
from bot.utils.dialog_menus import cancel as cancel_menu, privacy
from games.models import Punishment
from .PunishmentCreationStates import PunishmentCreationStates
from ...generate_session import bot
from ...models.AccessSettingsObject import AccessSettingsObject
from ...utils.dialog_texts import punishment_creation_texts

punishment_creation_router = Router()
punishment_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
punishment_creation_router.callback_query.filter(DialogAccessFilter(), DialogFilter("punishment_creation"))


@punishment_creation_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND))
async def create_punishment_command(message: Message, user: User, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()

    dialog = Dialog.create("punishment_creation", user_id=user.id, chat_id=message.chat.id, bot=bot)
    dialog.values["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    await dialog.send_message(punishment_creation_texts["name"], cancel_menu)
    await dialog.set_state(PunishmentCreationStates.choosing_name, context=state)
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@punishment_creation_router.message(StateFilter(PunishmentCreationStates.choosing_name), DialogAccessFilter(), F.content_type == ContentType.TEXT)
async def choose_name(message: Message, state: FSMContext, dialog: Dialog):
    await dialog.remove_state(context=state)
    dialog.values["name"] = message.text
    await dialog.delete_all_messages()
    await dialog.send_message(punishment_creation_texts["time"], cancel_menu)
    await dialog.set_state(PunishmentCreationStates.choosing_time, context=state)
    await message.delete()


@punishment_creation_router.message(StateFilter(PunishmentCreationStates.choosing_time),
                                    DialogAccessFilter(),
                                    F.text.regexp(r"\d+"),
                                    F.content_type == ContentType.TEXT)
async def choose_name(message: Message, member_settings: AccessSettingsObject, state: FSMContext, dialog: Dialog):
    await dialog.remove_state(context=state)

    matches = re.findall(r"\d+", message.text)
    days, hours, minutes = (0,) * (3 - len(matches)) + tuple(map(int, matches))
    time = timedelta(days=days, hours=hours, minutes=minutes)

    dialog.values["time"] = time.total_seconds()
    await dialog.delete_all_messages()
    await dialog.send_message(punishment_creation_texts["privacy"], privacy, menu_data={"settings": member_settings})
    await message.delete()


@punishment_creation_router.callback_query(ButtonFilter("privacy"))
async def choose_privacy(callback: CallbackQuery, user: User, chat: Chat, dialog_manager: DialogManager, dialog: Dialog, button: ButtonInstance):
    await callback.answer()
    public_indicator = button.data["public_indicator"]

    punishment = Punishment(name=dialog.values["name"],
                            time=timedelta(seconds=int(dialog.values["time"])),
                            created_by=user,
                            created_in=chat if public_indicator > -1 else None,
                            is_public=public_indicator == 1)
    await sync_to_async(lambda: punishment.clean())()
    await punishment.asave()

    await callback.message.answer(text=_("Punishment %(punishment)s successfully created") % {"punishment": punishment.get_string()})

    await dialog_manager.delete_dialog(dialog)
    await dialog.delete_all_messages()
