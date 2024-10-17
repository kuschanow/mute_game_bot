from aiogram.types import CallbackQuery
from aiogram_dialog_manager import Dialog
from asgiref.sync import sync_to_async

from bot.dialogs.dialog_menus import access_settings
from bot.dialogs.dialog_texts import access_settings_texts
from bot.models import Chat, AccessSettings


async def select_settings_target(callback: CallbackQuery, chat: Chat, dialog: Dialog, target_id: str, target: str, target_name: str):
    await callback.answer()

    query = AccessSettings.objects.filter(chat=chat, target=target, target_id=target_id)

    if not await query.aexists():
        settings_object = None
    else:
        _settings: AccessSettings = await query.afirst()
        settings_object = await sync_to_async(lambda: _settings.settings_object)()

    dialog.data["target"] = target
    dialog.data["target_name"] = target_name
    dialog.data["settings_object_id"] = str(settings_object.id) if settings_object else None

    await dialog.edit_message(callback.message.message_id,
                              access_settings_texts["base_settings"],
                              access_settings,
                              menu_data={"settings_object": settings_object})
