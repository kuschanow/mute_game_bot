import re
from datetime import timedelta

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog_manager import Dialog
from aiogram_dialog_manager.filter import DialogFilter, ButtonFilter, StateFilter
from aiogram_dialog_manager.instance import ButtonInstance, MessageInstance

from bot.filters import IsOwner
from bot.models import AccessSettingsObject
from bot.utils.dialog.dialog_buttons import access_time_settings
from bot.utils.dialog.dialog_menus import random_choice_game_access_settings
from .RandomChoiceGameAccessSettingsStates import RandomChoiceGameAccessSettingsStates

random_choice_game_access_settings_router = Router()
random_choice_game_access_settings_router.callback_query.filter(DialogFilter("access_settings"), IsOwner())
random_choice_game_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), IsOwner())


@random_choice_game_access_settings_router.callback_query(ButtonFilter(access_time_settings))
async def select_option(callback: CallbackQuery, state: FSMContext, dialog: Dialog, button: ButtonInstance):
    await callback.answer()
    await dialog.remove_state(context=state)
    await dialog.set_state(RandomChoiceGameAccessSettingsStates.get_by_string(button.data["type"]), context=state)

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.values["settings_object_id"])

    try:
        await dialog.edit_keyboard(callback.message.message_id,
                                   random_choice_game_access_settings,
                                   menu_data={"settings_object": settings_object, "highlight_this": button.data["type"]},
                                   message_marks={"target_time": button.data["type"]})
    except:
        pass


@random_choice_game_access_settings_router.message(StateFilter(RandomChoiceGameAccessSettingsStates.set_min_time), F.text.regexp(r"\d+"))
@random_choice_game_access_settings_router.message(StateFilter(RandomChoiceGameAccessSettingsStates.set_max_time), F.text.regexp(r"\d+"))
async def set_min_time(message: Message, state: FSMContext, dialog: Dialog):
    await dialog.remove_state(context=state)
    
    matches = re.findall(r"\d+", message.text)
    days, hours, minutes = (0,) * (3 - len(matches)) + tuple(map(int, matches))
    time = timedelta(days=days, hours=hours, minutes=minutes)

    time = min(max(time, timedelta(minutes=1)), timedelta(days=365))

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=dialog.values["settings_object_id"])

    dialog_message = dialog.messages[max(dialog.messages)]

    if dialog_message.marks["target_time"] == "min_time":
        settings_object.min_punish_time_for_rand_choice = time
    elif dialog_message.marks["target_time"] == "max_time":
        settings_object.max_punish_time_for_rand_choice = time

    dialog_message.marks.pop("target_time")

    await settings_object.asave()

    try:
        await dialog.edit_keyboard(dialog.values["main_message_id"],
                                   random_choice_game_access_settings,
                                   menu_data={"settings_object": settings_object})
    except:
        pass

    await message.delete()

