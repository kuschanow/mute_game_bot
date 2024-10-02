import re
from typing import Dict, Any

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter, StateFilter, DialogAccessFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils.translation import gettext as _

from bot.generate_session import bot
from bot.handlers.games.random_choice.GameSettingsStates import GameSettingsStates
from bot.handlers.games.random_choice.utils.texts import get_players
from bot.middlewares import set_random_choice_game_middlewares
from bot.models import ChatMember, User
from bot.dialogs.dialog_buttons import privacy, change_page, punishment, is_creator_play, min_max, losers, autostart_when_full, create, cancel
from bot.dialogs.dialog_menus import punishments, random_choice_settings, random_choice_game
from bot.dialogs.dialog_texts import random_choice_game_creation_texts, random_choice_game_texts
from games.models import RandomChoiceGame, RandomChoiceGamePlayer
from shared import category

game_creation_router = Router()
game_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
game_creation_router.callback_query.filter(DialogAccessFilter(), DialogFilter("random_choice_game_creation"))
set_random_choice_game_middlewares(game_creation_router)


@game_creation_router.message(Command(settings.RANDOM_CHOICE_GAME_COMMAND))
async def start_game_command(message: Message, member: ChatMember, user: User, dialog_manager: DialogManager,
                             state: FSMContext):
    await state.clear()

    if not member.access_settings.can_create_games:
        await message.answer(_("You cannot create games"))
        await message.delete()
        return

    dialog = Dialog.create("random_choice_game_creation", user_id=user.id, chat_id=message.chat.id, bot=bot)
    dialog.data["prefix"] = _("Dialog with ") + user.get_string(True) + "\n\n"
    dialog.data["public_indicator"] = 1
    dialog.data["category"] = category[1]
    dialog.data["page"] = 0

    menu_data = {
        "chat_member": member,
        "time_filters": member.access_settings.time_filters
    }

    bot_message = await dialog.send_message(random_choice_game_creation_texts["punishment"], punishments, menu_data=menu_data)
    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)
    await message.delete()


@game_creation_router.callback_query(ButtonFilter(privacy))
async def select_punishments_privacy(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, member: ChatMember):
    await callback.answer()

    dialog.data["public_indicator"] = button.data["public_indicator"]
    dialog.data["category"] = category[button.data["public_indicator"]]
    dialog.data["page"] = 0

    menu_data = {
        "chat_member": member,
        "time_filters": member.access_settings.time_filters
    }

    await dialog.edit_message(callback.message.message_id, random_choice_game_creation_texts["punishment"], punishments, menu_data=menu_data)


@game_creation_router.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, member: ChatMember):
    await callback.answer()
    dialog.data["page"] = button.data["page"]

    menu_data = {
        "chat_member": member,
        "time_filters": member.access_settings.time_filters
    }

    await dialog.edit_message(callback.message.message_id, random_choice_game_creation_texts["punishment"], punishments, menu_data=menu_data)


@game_creation_router.callback_query(ButtonFilter(punishment))
async def select_punishment(callback: CallbackQuery, member: ChatMember, dialog: Dialog, button: ButtonInstance):
    await callback.answer()
    game = RandomChoiceGame(punishment_id=button.data["id"],
                            creator=member,
                            autostart_at_max_players=True)
    await sync_to_async(lambda: game.clean())()
    await game.asave()
    dialog.data["game_id"] = str(game.id)
    dialog.data["game_text"] = await game.get_string()
    dialog.data["min"] = game.min_players_count
    dialog.data["max"] = game.max_players_count
    dialog.data["losers"] = game.losers_count

    await dialog.edit_message(callback.message.message_id, random_choice_game_creation_texts["settings"], random_choice_settings,
                              menu_data={"game": game, "member_settings": member.access_settings})


@game_creation_router.callback_query(ButtonFilter(is_creator_play))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, dialog: Dialog, member: ChatMember):
    await callback.answer()

    game.is_creator_playing = not game.is_creator_playing
    await game.asave()

    await dialog.edit_message(dialog.data["main_message_id"], random_choice_game_creation_texts["settings"], random_choice_settings,
                              menu_data={"game": game, "member_settings": member.access_settings})


@game_creation_router.callback_query(ButtonFilter(min_max))
@game_creation_router.callback_query(ButtonFilter(losers))
async def is_creator_play(callback: CallbackQuery, dialog: Dialog, state: FSMContext, button: ButtonInstance, member: ChatMember, game):
    await dialog.remove_state(context=state)
    await callback.answer(_("Send with your values"))

    await dialog.set_state(state=GameSettingsStates.get_by_string(button.type_name), context=state)

    try:
        await dialog.edit_keyboard(dialog.data["main_message_id"], random_choice_settings,
                                   menu_data={"game": game, "member_settings": member.access_settings, f"{button.type_name}_state": "selected"})
    except:
        pass


@game_creation_router.message(StateFilter(GameSettingsStates.set_min_max), F.text.regexp(r"(\d+|)-(\d+|)"))
async def set_min(message: Message, game: RandomChoiceGame, member: ChatMember, state: FSMContext, dialog: Dialog):
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

    dialog.data["min"] = game.min_players_count
    dialog.data["max"] = game.max_players_count
    dialog.data["losers"] = game.losers_count
    dialog.data["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.data["main_message_id"], random_choice_game_creation_texts["settings"], random_choice_settings,
                              menu_data={"game": game, "member_settings": member.access_settings})
    await message.delete()


@game_creation_router.message(StateFilter(GameSettingsStates.set_losers), F.text.regexp(r"\d+"))
async def set_losers(message: Message, game: RandomChoiceGame, member: ChatMember, state: FSMContext, dialog: Dialog):
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

    dialog.data["min"] = game.min_players_count
    dialog.data["max"] = game.max_players_count
    dialog.data["losers"] = game.losers_count
    dialog.data["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.data["main_message_id"], random_choice_game_creation_texts["settings"], random_choice_settings,
                              menu_data={"game": game, "member_settings": member.access_settings})
    await message.delete()


@game_creation_router.callback_query(ButtonFilter(autostart_when_full))
async def is_creator_play(callback: CallbackQuery, game: RandomChoiceGame, dialog: Dialog, member: ChatMember):
    await callback.answer()

    game.autostart_at_max_players = not game.autostart_at_max_players
    await game.asave()

    dialog.data["game_text"] = await game.get_string()

    await dialog.edit_message(dialog.data["main_message_id"], random_choice_game_creation_texts["settings"], random_choice_settings,
                              menu_data={"game": game, "member_settings": member.access_settings})


@game_creation_router.callback_query(ButtonFilter(create))
async def create(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember, dialog_manager: DialogManager, dialog: Dialog, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)

    game.is_opened_to_join = True
    await game.asave()

    if game.is_creator_playing and member.access_settings.can_join_games:
        await RandomChoiceGamePlayer(game=game, chat_member=member).asave()

    dialog = Dialog.create("random_choice_game", user_id=member.user_id, chat_id=member.chat_id, bot=bot)

    dialog.data["game_id"] = str(game.id)
    dialog.data["game_text"] = await game.get_string()
    dialog.data["game_players"] = await get_players(game)

    bot_message = await dialog.send_message(random_choice_game_texts["game"], random_choice_game, menu_data={"game": game})

    dialog.data["main_message_id"] = bot_message.message_id
    await dialog_manager.save_dialog(dialog)


@game_creation_router.callback_query(ButtonFilter(cancel))
async def cancel(callback: CallbackQuery, dialog: Dialog, state: FSMContext, dialog_manager: DialogManager, game: RandomChoiceGame = None):
    await callback.answer(_("Ok"))
    await dialog.remove_state(context=state)
    if game:
        await game.adelete()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
