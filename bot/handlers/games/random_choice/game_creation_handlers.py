from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from django.conf import settings
from django.utils.translation import gettext as _

from bot.models import ChatMember
from .Dialog import Dialog
from .keyboards import get_punishment_categories_keyboard, get_punishments_keyboard

game_handlers_router = Router()
game_handlers_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_handlers_router.callback_query.filter(F.data.startswith("rcgc"))


@game_handlers_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember, state: FSMContext):
    dialog = Dialog()

    data = await state.get_data()
    if "dialogs" not in data:
        data["dialogs"] = {}
    data["dialogs"][dialog.dialog_id] = dialog.to_dict()
    await state.set_data(data)

    await message.answer(text=_("Choose a punishment category from the list below"),
                         reply_markup=get_punishment_categories_keyboard(dialog.dialog_id))
    await message.delete()


@game_handlers_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember, state: FSMContext):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[2]
    page = int(callback_data[1])
    is_public = bool(int(callback_data[0]))
    keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, is_public, page)

    data = await state.get_data()
    dialog = Dialog.from_dict(data["dialogs"][dialog_id])
    dialog.set_punishment_menu_mapping(punishments_mapping)

    data["dialogs"][dialog_id] = dialog.to_dict()

    await state.set_data(data)

    # Translators: punishment selection dialogue
    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": _("Public") if is_public else _("Private")}),
                                     reply_markup=keyboard)

@game_handlers_router.callback_query(F.data.contains("p_select"))
async def select_punishment(callback: CallbackQuery, state: FSMContext):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[1]
    punish_num = int(callback_data[0])

    data = await state.get_data()
    dialog = Dialog.from_dict(data["dialogs"][dialog_id])
    dialog.select_punishment(punish_num)

    data["dialogs"].pop(dialog_id)
    await state.set_data(data)

    # Translators: random choice game dialogue
    await callback.message.edit_text(text=_("А на этом пока всё"))


