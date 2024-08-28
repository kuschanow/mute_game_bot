from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import DialogAccess
from bot.models import ChatMember
from bot.models.AccessSettingsObject import AccessSettingsObject
from games.models import RandomChoiceGame
from shared import redis, category
from .GameCreationDialog import GameCreationDialog
from .utils.keyboards import get_punishments_keyboard, get_game_settings_keyboard

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(F.data.startswith("rcgc"), DialogAccess())


@game_creation_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember, member_settings: AccessSettingsObject, state: FSMContext):
    if not member_settings.can_create_games:
        await message.answer(_("You cannot create games"))
        await message.delete()
        return

    await state.clear()

    dialog = GameCreationDialog()

    data = await redis.get_or_set(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {}

    keyboard, punishments_mapping = await get_punishments_keyboard(dialog.dialog_id, member, member_settings, 1, 1)
    dialog.set_punishment_menu_mapping(punishments_mapping)
    data["dialogs"][dialog.dialog_id] = dialog.to_dict()
    await redis.set_serialized(str(member.id), data)

    await message.answer(text=_("Choose a punishment from the list below\n\n"
                                "Category: %(category)s" % {"category": _("Public")}),
                         reply_markup=keyboard)
    await message.delete()


@game_creation_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[2]
    page = int(callback_data[1])
    public_indicator = int(callback_data[0])
    keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, member_settings, public_indicator, page)

    data = await redis.get_deserialized(str(member.id))
    dialog = GameCreationDialog.from_dict(data["dialogs"][dialog_id])
    dialog.set_punishment_menu_mapping(punishments_mapping)

    data["dialogs"][dialog_id] = dialog.to_dict()

    await redis.set_serialized(str(member.id), data)

    # Translators: punishment selection dialogue
    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": category[public_indicator]}),
                                     reply_markup=keyboard)

@game_creation_router.callback_query(F.data.contains("p_select"))
async def select_punishment(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[1]
    punish_num = int(callback_data[0])

    data = await redis.get_deserialized(str(member.id))
    dialog = GameCreationDialog.from_dict(data["dialogs"][dialog_id])
    dialog.select_punishment(punish_num)

    game = RandomChoiceGame(punishment_id=dialog.punishment_id,
                            creator=member)
    await sync_to_async(lambda: game.clean())()
    await game.asave()

    data["dialogs"].pop(dialog_id)
    data["dialogs"][str(game.id)] = {"date": str(datetime.utcnow()), "message_id": callback.message.message_id}
    await redis.set_serialized(str(member.id), data)

    # Translators: random choice game dialogue
    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))


@game_creation_router.callback_query(F.data.contains("cancel"))
async def cancel(callback: CallbackQuery, member: ChatMember):
    dialog_id = callback.data.split(':')[-1]

    user_data = await redis.get_deserialized(str(member.id))
    user_data["dialogs"].pop(dialog_id)

    await redis.set_serialized(str(member.id), user_data)

    await callback.answer(_("Ok"))
    await callback.message.delete()

