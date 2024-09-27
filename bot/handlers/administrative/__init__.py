from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from aiogram_dialog_manager import DialogManager, Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter
from aiogram_dialog_manager.instance import ButtonInstance

from shared import dialog_storage
from bot.generate_session import bot

from .access_settings import access_settings_router
from ...models import AccessSettingsObject
from ...utils.dialog.dialog_menus import settings_target, access_settings, game_settings_select
from ...utils.dialog.dialog_texts import access_settings_texts

administrative_router = Router()
administrative_router.callback_query.filter(DialogFilter("access_settings"))

administrative_dialog_manager = DialogManager(storage=dialog_storage, router=administrative_router, bot=bot)

administrative_router.include_routers(access_settings_router)


@administrative_router.callback_query(ButtonFilter("back"))
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

