from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.filter import ButtonFilter, DialogAccessFilter
from aiogram_dialog_manager.instance import ButtonInstance

from bot.dialogs.dialog_buttons import privacy, change_page
from bot.dialogs.dialog_menus import punishments
from bot.dialogs.dialog_texts import game_creation_texts
from bot.middlewares.games_middleware import set_random_choice_game_middlewares
from bot.models import ChatMember, AccessSettingsObject
from shared import category

punishment_selection_router = Router()
punishment_selection_router.callback_query.filter(DialogAccessFilter())
set_random_choice_game_middlewares(punishment_selection_router)


@punishment_selection_router.callback_query(ButtonFilter(privacy))
async def select_punishments_privacy(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, member: ChatMember,
                                     access_settings: AccessSettingsObject):
    await callback.answer()

    dialog.data["public_indicator"] = button.data["public_indicator"]
    dialog.data["category"] = category[button.data["public_indicator"]]
    dialog.data["page"] = 0

    menu_data = {
        "chat_member": member,
        "time_filters": access_settings.time_filters
    }

    await dialog.edit_message(callback.message.message_id, game_creation_texts["punishment"], punishments, menu_data=menu_data)


@punishment_selection_router.callback_query(ButtonFilter(change_page))
async def select_page(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, member: ChatMember, access_settings: AccessSettingsObject):
    await callback.answer()
    dialog.data["page"] = button.data["page"]

    menu_data = {
        "chat_member": member,
        "time_filters": access_settings.time_filters
    }

    await dialog.edit_message(callback.message.message_id, game_creation_texts["punishment"], punishments, menu_data=menu_data)
