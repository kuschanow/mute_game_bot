from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog, DialogManager
from aiogram_dialog_manager.filter import DialogFilter, DialogAccessFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance
from asgiref.sync import sync_to_async

from bot.dialogs.dialog_buttons import cell
from bot.dialogs.dialog_texts import hidden_mines_game_texts
from bot.handlers.games.utils import mute_losers
from bot.middlewares.games_middleware import set_hidden_mines_game_middlewares
from games.models import HiddenMinesGame
from shared.enums.CellTypes import CellTypes

cells_router = Router()
cells_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
cells_router.callback_query.filter(DialogAccessFilter(), DialogFilter("hidden_mines_game"))
set_hidden_mines_game_middlewares(cells_router)


@cells_router.callback_query(ButtonFilter(cell, type=CellTypes.WIN))
async def open_win_cell(callback: CallbackQuery, game: HiddenMinesGame, dialog_manager: DialogManager, dialog: Dialog, button: ButtonInstance):
    await callback.answer()

    opened_cell = game.field.cells.get(id=button.data["id"])

    result = await game.finish_game(opened_cell)

    dialog.data["game_result"] = await sync_to_async(result.get_string)()

    await dialog.edit_message(dialog.data["main_message"], hidden_mines_game_texts["results"])

    await dialog_manager.delete_dialog(dialog)


@cells_router.callback_query(ButtonFilter(cell, type=CellTypes.MINE))
async def open_win_cell(callback: CallbackQuery, game: HiddenMinesGame, dialog_manager: DialogManager, dialog: Dialog, button: ButtonInstance, chat):
    await callback.answer()

    opened_cell = game.field.cells.get(id=button.data["id"])

    result = await game.finish_game(opened_cell)

    dialog.data["game_result"] = await sync_to_async(result.get_string)()

    await dialog.edit_message(dialog.data["main_message"], hidden_mines_game_texts["results"])

    await dialog_manager.delete_dialog(dialog)

    await mute_losers(game, chat)
