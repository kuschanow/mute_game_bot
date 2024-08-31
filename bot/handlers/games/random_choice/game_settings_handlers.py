import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.utils.translation import gettext as _

from bot.filters import DialogAccess
from bot.filters.ReplyToCorrectMessage import ReplyToCorrectMessage
from bot.handlers.games.random_choice.GameSettingsStates import GameSettingsStates
from bot.handlers.games.random_choice.utils.keyboards import get_game_settings_keyboard, get_game_menu_keyboard
from bot.handlers.games.random_choice.utils.texts import get_players
from bot.middlewares import set_random_choice_game_middlewares
from bot.models import AccessSettingsObject, ChatMember
from games.models import RandomChoiceGame, RandomChoiceGamePlayer
from shared import redis

game_settings_router = Router()
game_settings_router.callback_query.filter(F.data.startswith("rcgs"), DialogAccess())
game_settings_router.message.filter(ReplyToCorrectMessage("message_id"))
set_random_choice_game_middlewares(game_settings_router)


async def update_message(message, game, member_settings):
    try:
        await message.edit_text(
            text=await game.get_string(),
            reply_markup=get_game_settings_keyboard(game, member_settings)
        )
    except:
        pass


@game_settings_router.callback_query(F.data.contains("is_creator_play"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    await state.clear()

    if not member_settings.can_join_games:
        await callback.answer(_("You are not allowed to join the games"))
        return

    game.is_creator_playing = not game.is_creator_playing
    await game.asave()

    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))

    await callback.answer()


@game_settings_router.callback_query(F.data.contains("min_max"))
@game_settings_router.callback_query(F.data.contains("losers"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    await state.clear()

    await state.set_data({"message_id": callback.message.message_id, "game_id": str(game.id)})

    button = callback.data.split(":")[-2]

    await state.set_state(GameSettingsStates.get_be_string(button))

    try:
        await callback.message.edit_text(text=callback.message.text, reply_markup=get_game_settings_keyboard(game, member_settings, button))
    except:
        pass

    await callback.answer(_("Reply with your values"))


@game_settings_router.message(GameSettingsStates.set_min_max, F.text.regexp(r"(\d+|)-(\d+|)"))
async def set_min(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    min_str, max_str = re.search(r"(\d+|)-(\d+|)", message.text).groups()

    min_num = int(min_str) if min_str else 2
    max_num = int(max_str) if max_str else None

    if max_num:
        max_num = max_num if max_num >= 2 else 2
        if min_num > max_num:
            max_num, min_num = min_num, max_num

    min_num = min_num if min_num >= 2 else 2

    game.min_players_count = min_num
    game.losers_count = min(min_num - 1, game.losers_count)
    game.max_players_count = max_num
    await game.asave()

    await state.clear()
    await update_message(message.reply_to_message, game, member_settings)
    await message.delete()


@game_settings_router.message(GameSettingsStates.set_losers, F.text.regexp(r"\d+"))
async def set_losers(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    number = int(re.search(r"\d+", message.text).group())

    if number <= 0:
        number = 1

    if number > game.min_players_count:
        game.min_players_count = number + 1
    if game.max_players_count and number >= game.max_players_count:
        game.max_players_count = number + 1

    game.losers_count = number
    await game.asave()
    await update_message(message.reply_to_message, game, member_settings)
    await state.clear()

    await message.delete()


@game_settings_router.callback_query(F.data.contains("when_full"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    await state.clear()

    if game.max_players_count is None:
        await callback.answer(_("Cannot be installed if the maximum number of players is not set"))
        return

    game.autostart_at_max_players = not game.autostart_at_max_players
    await game.asave()

    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))

    await callback.answer()


@game_settings_router.callback_query(F.data.contains("create"))
async def create(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember, member_settings: AccessSettingsObject, state: FSMContext):
    await state.clear()
    game.is_opened_to_join = True
    await game.asave()

    if game.is_creator_playing and member_settings.can_join_games:
        await RandomChoiceGamePlayer(game=game, chat_member=member).asave()

    await redis.set_serialized(str(game.id), {"messages": [callback.message.message_id]})

    await callback.message.edit_text(text=await get_players(game), reply_markup=await get_game_menu_keyboard(game))
    await callback.answer()


@game_settings_router.callback_query(F.data.contains("cancel_creation"))
async def cancel_creation(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember):
    data = await redis.get_deserialized(str(member.id))
    data["dialogs"].pop(str(callback.message.message_id))
    await redis.set_serialized(str(member.id), data)

    await game.adelete()

    await callback.message.delete()
    await callback.answer()

