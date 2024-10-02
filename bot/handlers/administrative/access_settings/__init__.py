from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance

from bot.dialogs.dialog_menus import settings_target, access_settings, game_settings_select, access_groups
from bot.dialogs.dialog_texts import access_settings_texts
from .games_settings import games_settings_router
from .main_access_settings import main_access_settings_router
from bot.models import AccessSettingsObject

access_settings_router = Router()
access_settings_router.callback_query.filter(DialogFilter("access_settings"))

access_settings_router.include_routers(games_settings_router, main_access_settings_router)

@access_settings_router.callback_query(ButtonFilter("cancel"))
async def cancel(callback: CallbackQuery, state: FSMContext, dialog: Dialog, dialog_manager: DialogManager):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.delete_all_messages()
    await dialog_manager.delete_dialog(dialog)


@access_settings_router.callback_query(ButtonFilter("back"))
async def back(callback: CallbackQuery, dialog: Dialog, button: ButtonInstance, state: FSMContext):
    await callback.answer()
    await dialog.remove_state(context=state)

    if button.data["page"] == "target":
        await dialog.edit_message(callback.message.message_id, access_settings_texts["target"], settings_target)
    elif button.data["page"] == "main_settings":
        settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.values["settings_object_id"])

        await dialog.edit_message(callback.message.message_id,
                                  access_settings_texts["base_settings"],
                                  access_settings,
                                  menu_data={"settings_object": settings_object})
    elif button.data["page"] == "game_menu":
        await dialog.edit_message(callback.message.message_id, access_settings_texts["base_settings"], game_settings_select)
    elif button.data["page"] == "access_groups":
        await dialog.edit_message(callback.message.message_id, access_settings_texts["base_settings"], access_groups)
