from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.types import Message, CallbackQuery
from django.conf import settings
from django.utils.translation import gettext as _

from bot.filters import DialogAccessFilter
from bot.models import ChatMember
from games.models import RandomChoiceGame, RandomChoiceGamePlayer
from shared import redis
from .GameCreationDialog import GameCreationDialog
from .utils.keyboards import get_punishments_keyboard, get_game_menu_keyboard
from .utils.texts import get_players

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(F.data.startswith("rcgc"), DialogAccessFilter())


@game_creation_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember):
    dialog = GameCreationDialog()

    data = await redis.get_or_set(str(member.id))
    if "dialogs" not in data:
        data["dialogs"] = {}

    keyboard, punishments_mapping = await get_punishments_keyboard(dialog.dialog_id, member, 1, 1)
    dialog.set_punishment_menu_mapping(punishments_mapping)
    data["dialogs"][dialog.dialog_id] = dialog.to_dict()
    await redis.set_serialized(str(member.id), data)

    await message.answer(text=_("Choose a punishment from the list below\n\n"
                                "Category: %(category)s" % {"category": _("Public")}),
                         reply_markup=keyboard)
    await message.delete()


@game_creation_router.callback_query(F.data.contains("p_category"))
async def select_punishments_category(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[2]
    page = int(callback_data[1])
    public_indicator = int(callback_data[0])
    keyboard, punishments_mapping = await get_punishments_keyboard(dialog_id, member, public_indicator, page)

    data = await redis.get_deserialized(str(member.id))
    dialog = GameCreationDialog.from_dict(data["dialogs"][dialog_id])
    dialog.set_punishment_menu_mapping(punishments_mapping)

    data["dialogs"][dialog_id] = dialog.to_dict()

    await redis.set_serialized(str(member.id), data)

    category = {
        -1: _("Private Global"),
        0: _("Private Local"),
        1: _("Public")
    }

    # Translators: punishment selection dialogue
    await callback.message.edit_text(text=_("Choose a punishment from the list below\n\n"
                                            "Category: %(category)s" % {"category": category[public_indicator]}),
                                     reply_markup=keyboard)

@game_creation_router.callback_query(F.data.contains("p_select"))
async def select_punishment(callback: CallbackQuery, member: ChatMember):
    callback_data = callback.data.split(':')[2:]
    dialog_id = callback_data[1]
    punish_num = int(callback_data[0])

    data = await redis.get_deserialized(str(member.id))
    dialog = GameCreationDialog.from_dict(data["dialogs"][dialog_id])
    dialog.select_punishment(punish_num)

    game = RandomChoiceGame(punishment_id=dialog.punishment_id,
                            creator=member)
    await game.asave()

    if game.is_creator_playing:
        await RandomChoiceGamePlayer(game=game, chat_member=member).asave()

    data["dialogs"].pop(dialog_id)
    await redis.set_serialized(str(member.id), data)

    await redis.set_serialized(str(game.id), {"messages": [callback.message.message_id]})

    # Translators: random choice game dialogue
    await callback.message.edit_text(text=await get_players(game), reply_markup=await get_game_menu_keyboard(game))

@game_creation_router.callback_query(F.data.contains("cancel"))
async def cancel(callback: CallbackQuery, member: ChatMember):
    dialog_id = callback.data.split(':')[-1]

    user_data = await redis.get_deserialized(str(member.id))
    user_data["dialogs"].pop(dialog_id)

    await redis.set_serialized(str(member.id), user_data)

    await callback.answer(_("Ok"))
    await callback.message.delete()

