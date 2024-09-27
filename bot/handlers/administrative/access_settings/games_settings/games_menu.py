from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.filter import ButtonFilter, DialogFilter
from django.utils.translation import gettext as _

from bot.filters import IsOwner
from bot.models import AccessSettingsObject
from bot.utils.dialog.dialog_buttons import game_access_settings
from bot.utils.dialog.dialog_menus import random_choice_game_access_settings
from bot.utils.dialog.dialog_texts import access_settings_texts

games_menu_router = Router()
games_menu_router.callback_query.filter(DialogFilter("access_settings"), IsOwner())


@games_menu_router.callback_query(ButtonFilter(game_access_settings, game="random_choice_game"))
async def random_choice_game(callback: CallbackQuery, dialog: Dialog):
    await callback.answer()

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.data["settings_object_id"])

    dialog.data["game"] = "random_choice_game"
    dialog.data["game_name"] = _("Random choice game")

    await dialog.edit_message(callback.message.message_id, access_settings_texts["game_settings"], random_choice_game_access_settings, menu_data={"settings_object": settings_object})

