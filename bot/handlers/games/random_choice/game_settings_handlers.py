import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django.utils.translation import gettext as _

from bot.filters import DialogAccess
from bot.filters.ReplyToCorrectMessage import ReplayToCorrectMessage
from bot.handlers.games.random_choice.GameSettingsStates import GameSettingsStates
from bot.handlers.games.random_choice.utils.keyboards import get_game_settings_keyboard, get_game_menu_keyboard
from bot.handlers.games.random_choice.utils.texts import get_players
from bot.middlewares import set_random_choice_game_middlewares
from bot.models import AccessSettingsObject, ChatMember
from games.models import RandomChoiceGame, RandomChoiceGamePlayer
from shared import redis

game_settings_router = Router()
game_settings_router.callback_query.filter(F.data.startswith("rcgs"), DialogAccess())
game_settings_router.message.filter(ReplayToCorrectMessage("message_id"))
set_random_choice_game_middlewares(game_settings_router)


@game_settings_router.callback_query(F.data.contains("is_creator_play"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, member_settings: AccessSettingsObject):
    if not member_settings.can_join_games:
        await callback.answer(_("You are not allowed to join the games"))
        return

    game.is_creator_playing = not game.is_creator_playing
    await game.asave()

    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))

    await callback.answer()


@game_settings_router.callback_query(F.data.contains("min"))
@game_settings_router.callback_query(F.data.contains("max"))
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

    await callback.answer(_("Replay with int number"))


@game_settings_router.message(GameSettingsStates.set_min, F.text.regexp(r"\d+"))
async def set_min(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    number = int(re.search(r"\d+", message.text).group())

    if 2 <= number <= game.max_players_count:
        game.min_players_count = number
        if game.losers_count >= number:
            game.losers_count = number - 1
        await game.asave()
        try:
            await message.reply_to_message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))
        except:
            pass
        await state.clear()
        
    await message.delete()


@game_settings_router.message(GameSettingsStates.set_max, F.text.regexp(r"\d+|-"))
async def set_max(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    if re.search(r"\d+", message.text).group() == "-":
        game.max_players_count = None
        await game.asave()
        try:
            await message.reply_to_message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))
        except:
            pass
        await state.clear()

    number = int(re.search(r"\d+", message.text).group())

    if game.min_players_count <= number:
        game.max_players_count = number
        await game.asave()
        try:
            await message.reply_to_message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))
        except:
            pass
        await state.clear()

    await message.delete()


@game_settings_router.message(GameSettingsStates.set_losers, F.text.regexp(r"\d+"))
async def set_losers(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext):
    number = int(re.search(r"\d+", message.text).group())

    if 0 < number < game.min_players_count:
        game.losers_count = number
        await game.asave()
        try:
            await message.reply_to_message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))
        except:
            pass
        await state.clear()

    await message.delete()


@game_settings_router.callback_query(F.data.contains("when_full"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, member_settings: AccessSettingsObject):
    if game.max_players_count is None:
        await callback.answer(_("Cannot be installed if the maximum number of players is not set"))
        return

    game.autostart_at_max_players = not game.autostart_at_max_players
    await game.asave()

    await callback.message.edit_text(text=await game.get_string(), reply_markup=get_game_settings_keyboard(game, member_settings))

    await callback.answer()


@game_settings_router.callback_query(F.data.contains("create"))
async def create(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember, member_settings: AccessSettingsObject):
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
    data["dialogs"].pop(str(game.id))
    await redis.set_serialized(str(member.id), data)

    await game.adelete()

    await callback.message.delete()
    await callback.answer()

