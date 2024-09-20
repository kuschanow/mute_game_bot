from aiogram import Router, F
from aiogram.filters import MagicData
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import DialogManager
from aiogram_dialog_manager.instance import Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.filter.access import DialogAccessFilter
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from bot.middlewares import set_random_choice_game_middlewares
from bot.models import ChatMember, Chat
from bot.models.AccessSettingsObject import AccessSettingsObject
from bot.utils.dialog_menus import random_choice_game
from bot.utils.dialog_texts import random_choice_game_texts
from games.models import RandomChoiceGame, RandomChoiceGamePlayer, RandomChoiceGameResult
from .utils.texts import get_players, get_losers
from ..utils import mute_losers

game_router = Router()
game_router.callback_query.filter(DialogFilter("random_choice_game"))
set_random_choice_game_middlewares(game_router)


@game_router.callback_query(ButtonFilter("join"))
async def join_game(callback: CallbackQuery, game: RandomChoiceGame, member: ChatMember, member_settings: AccessSettingsObject, chat: Chat, dialog: Dialog, dialog_manager: DialogManager):
    if game.creator_id == member.id:
        await callback.answer(_("The creator cannot leave or join their game"))
        return

    if not member_settings.can_join_games:
        await callback.answer(_("You cannot join games"))
        return

    if await sync_to_async(lambda: member in game.players.all())():
        await sync_to_async(game.players.remove)(member)
        await callback.answer(_("You left the game"))
    else:
        if await game.players.acount() < game.max_players_count:
            await RandomChoiceGamePlayer(game=game, chat_member=member).asave()
            await callback.answer(_("You join the game"))
        else:
            await callback.answer(_("The game already has the maximum number of players"))
            return

    dialog.values["game_text"] = await game.get_string()
    dialog.values["game_players"] = await get_players(game)

    await dialog.edit_message(callback.message.message_id, random_choice_game_texts["game"], random_choice_game, menu_data={"game": game})

    if game.autostart_at_max_players and await game.players.acount() == game.max_players_count:
        result: RandomChoiceGameResult = await game.start_game()

        await mute_losers(game, result, chat)

        await dialog.edit_message(callback.message.message_id, random_choice_game_texts["game"])
        dialog.values["game_losers"] = await get_losers(result)
        await dialog.send_message(random_choice_game_texts["results"], reply_to_message_id=callback.message.message_id)
        await dialog_manager.delete_dialog(dialog)


@game_router.callback_query(ButtonFilter("start"), MagicData(F.member_settings.can_press_other_buttons.is_(True)))
@game_router.callback_query(ButtonFilter("start"), DialogAccessFilter())
async def start_game(callback: CallbackQuery, game: RandomChoiceGame, chat: Chat, dialog: Dialog, dialog_manager: DialogManager):
    if await game.players.acount() < game.min_players_count:
        await callback.answer(_("There are not enough players in the game"))
        return

    result: RandomChoiceGameResult = await game.start_game()

    await mute_losers(game, result, chat)

    await dialog.edit_message(callback.message.message_id, random_choice_game_texts["game"])
    dialog.values["game_losers"] = await get_losers(result)
    await dialog.send_message(random_choice_game_texts["results"], reply_to_message_id=callback.message.message_id)
    await dialog_manager.delete_dialog(dialog)


@game_router.callback_query(ButtonFilter("delete"), MagicData(F.member_settings.can_press_other_buttons.is_(True)))
@game_router.callback_query(ButtonFilter("delete"), DialogAccessFilter())
async def delete_game(callback: CallbackQuery, game: RandomChoiceGame, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer(_("Deleted successfully"))
    await game.adelete()
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)
