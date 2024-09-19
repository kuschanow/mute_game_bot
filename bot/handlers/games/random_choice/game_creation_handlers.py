import re
from typing import Dict, Any

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import DialogManager, DialogInstance, DialogMessage
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter, StateFilter
from aiogram_dialog_manager.filter.access import DialogAccessFilter
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.handlers.games.random_choice.GameSettingsStates import GameSettingsStates
from bot.handlers.games.random_choice.utils.keyboards import get_settings_keyboard, get_game_menu_keyboard
from bot.handlers.games.random_choice.utils.texts import get_players
from bot.middlewares import set_random_choice_game_middlewares
from bot.models import ChatMember, User
from bot.models.AccessSettingsObject import AccessSettingsObject
from bot.utils.punishment_selection_keyboard import get_punishments_keyboard
from games.models import RandomChoiceGame, RandomChoiceGamePlayer
from shared import category

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(DialogAccessFilter(), DialogFilter("game_creation"))
set_random_choice_game_middlewares(game_creation_router)


@game_creation_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember, user: User, member_settings: AccessSettingsObject, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()

    if not member_settings.can_create_games:
        await message.answer(_("You cannot create games"))
        await message.delete()
        return

    dialog: DialogInstance = dialog_manager.create_dialog(prototype_name="game_creation", user_id=user.id, chat_id=message.chat.id)
    dialog.values["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    dialog.values["public_indicator"] = 1
    dialog.values["category"] = category[1]
    dialog.values["page"] = 0
    bot_message = await dialog.send_message("punishment",
                              await get_punishments_keyboard(member, member_settings, 1, 0, {"time__lte": member_settings.max_punish_time_for_rand_choice,
                                                                                             "time__gte": member_settings.min_punish_time_for_rand_choice}))
    dialog.values["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@game_creation_router.callback_query(ButtonFilter("privacy"))
async def select_punishments_privacy(callback: CallbackQuery, dialog: DialogInstance, button_data: Dict[str, Any], member, member_settings):
    await callback.answer()
    keyboard = await get_punishments_keyboard(member, member_settings, button_data["public_indicator"], 0, {"time__lte": member_settings.max_punish_time_for_rand_choice,
                                                                                                            "time__gte": member_settings.min_punish_time_for_rand_choice})
    dialog.values["public_indicator"] = button_data["public_indicator"]
    dialog.values["category"] = category[button_data["public_indicator"]]
    dialog.values["page"] = 0
    await dialog.edit_message(callback.message.message_id, "punishment", keyboard)


@game_creation_router.callback_query(ButtonFilter("change_page"))
async def select_page(callback: CallbackQuery, dialog: DialogInstance, button_data: Dict[str, Any], member, member_settings):
    await callback.answer()
    keyboard = await get_punishments_keyboard(member, member_settings, dialog.values["public_indicator"], button_data["page"], {"time__lte": member_settings.max_punish_time_for_rand_choice,
                                                                                                                                "time__gte": member_settings.min_punish_time_for_rand_choice})
    dialog.values["page"] = button_data["page"]
    await dialog.edit_message(callback.message.message_id, "punishment", keyboard)


@game_creation_router.callback_query(ButtonFilter("punishment"))
async def select_punishment(callback: CallbackQuery, member: ChatMember, member_settings: AccessSettingsObject, dialog: DialogInstance, button_data: Dict[str, Any]):
    await callback.answer()
    game = RandomChoiceGame(punishment_id=button_data["id"],
                            creator=member,
                            autostart_at_max_players=True)
    await sync_to_async(lambda: game.clean())()
    await game.asave()
    dialog.values["game_id"] = str(game.id)
    dialog.values["game_text"] = await game.get_string()
    dialog.values["min"] = game.min_players_count
    dialog.values["max"] = game.max_players_count
    dialog.values["losers"] = game.losers_count

    await dialog.edit_message(callback.message.message_id, "settings", get_settings_keyboard(game, member_settings))


@game_creation_router.callback_query(ButtonFilter("is_creator_play"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, dialog: DialogInstance, dialog_message: DialogMessage):
    await callback.answer()

    game.is_creator_playing = not game.is_creator_playing
    await game.asave()

    menu = dialog_message.reuse_menu()
    menu[0][0][1]["value"] = game.is_creator_playing

    await dialog.edit_message(dialog_message.message_id, "settings", menu)


@game_creation_router.callback_query(ButtonFilter("min_max"))
@game_creation_router.callback_query(ButtonFilter("losers"))
async def is_creator_play(callback: CallbackQuery, dialog: DialogInstance, dialog_message: DialogMessage, state: FSMContext, button_info: Dict[str, Any]):
    await dialog.remove_state(context=state)
    await callback.answer(_("Send with your values"))

    menu = dialog_message.reuse_menu()
    row, button = dialog_message.get_button_position(callback.data[2:])
    menu[row][button][1]["state"] = "selected"

    await dialog.set_state(state=GameSettingsStates.get_by_string(button_info["button"]), context=state)

    try:
        await dialog.edit_keyboard(dialog_message.message_id, menu)
    except:
        pass


@game_creation_router.message(StateFilter(GameSettingsStates.set_min_max), F.text.regexp(r"(\d+|)-(\d+|)"))
async def set_min(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext, dialog: DialogInstance):
    await dialog.remove_state(context=state)
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

    dialog.values["min"] = game.min_players_count
    dialog.values["max"] = game.max_players_count
    dialog.values["losers"] = game.losers_count
    dialog.values["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.values["main_message_id"], "settings", get_settings_keyboard(game, member_settings))
    await message.delete()


@game_creation_router.message(StateFilter(GameSettingsStates.set_losers), F.text.regexp(r"\d+"))
async def set_losers(message: Message, game: RandomChoiceGame, member_settings: AccessSettingsObject, state: FSMContext, dialog: DialogInstance):
    await dialog.remove_state(context=state)
    number = int(re.search(r"\d+", message.text).group())

    if number <= 0:
        number = 1

    if number >= game.min_players_count:
        game.min_players_count = number + 1
    if game.max_players_count and number >= game.max_players_count:
        game.max_players_count = number + 1

    game.losers_count = number
    await game.asave()

    dialog.values["min"] = game.min_players_count
    dialog.values["max"] = game.max_players_count
    dialog.values["losers"] = game.losers_count
    dialog.values["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.values["main_message_id"], "settings", get_settings_keyboard(game, member_settings))
    await message.delete()


@game_creation_router.callback_query(ButtonFilter("autostart_when_full"))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, dialog: DialogInstance, dialog_message: DialogMessage):
    await callback.answer()

    game.autostart_at_max_players = not game.autostart_at_max_players
    await game.asave()

    menu = dialog_message.reuse_menu()
    menu[-3][0][1]["value"] = game.autostart_at_max_players

    dialog.values["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.values["main_message_id"], "settings", menu)


@game_creation_router.callback_query(ButtonFilter("create"))
async def create(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember, dialog_manager: DialogManager, dialog: DialogInstance, member_settings: AccessSettingsObject, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)

    game.is_opened_to_join = True
    await game.asave()

    if game.is_creator_playing and member_settings.can_join_games:
        await RandomChoiceGamePlayer(game=game, chat_member=member).asave()

    dialog = dialog_manager.create_dialog("game_dialog", int(member.user_id), int(member.chat_id))

    dialog.values["game_id"] = str(game.id)
    dialog.values["game_text"] = await game.get_string()
    dialog.values["game_players"] = await get_players(game)

    bot_message = await dialog.send_message("game", await get_game_menu_keyboard(game))

    dialog.values["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)


@game_creation_router.callback_query(ButtonFilter("cancel"))
async def cancel(callback: CallbackQuery, dialog: DialogInstance, state: FSMContext, dialog_manager: DialogManager, game: RandomChoiceGame=None):
    await callback.answer(_("Ok"))
    await dialog.remove_state(context=state)
    if game:
        await game.adelete()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)


