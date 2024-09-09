import re
import uuid
from datetime import timedelta

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.filters import IsOwner
from bot.generate_session import bot
from shared import redis
from .RandomChoiceGameAccessSettingsStates import RandomChoiceGameAccessSettingsStates
from bot.models import Chat, AccessSettingsObject, ChatMember
from ..utils.access_settings_keyboards import get_random_choice_game_settings_keyboard

random_choice_game_access_settings_router = Router()
random_choice_game_access_settings_router.callback_query.filter(F.data.startswith("stgs:games:rcg"), IsOwner())
random_choice_game_access_settings_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)), IsOwner())


@random_choice_game_access_settings_router.callback_query(F.data.contains("min_time"))
@random_choice_game_access_settings_router.callback_query(F.data.contains("max_time"))
async def select_option(callback: CallbackQuery, member: ChatMember, state: FSMContext):
    data = await redis.get_deserialized(str(member.id))
    settings_object_id = uuid.UUID(data["dialogs"][str(callback.message.message_id)]["settings_object_id"])
    target_id = callback.data.split(":")[3]
    state_name = callback.data.split(":")[-1]

    await state.clear()
    await state.set_state(RandomChoiceGameAccessSettingsStates.get_by_string(state_name))
    await state.set_data({"message_id": callback.message.message_id, "target_id": target_id})

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=settings_object_id)

    try:
        await callback.message.edit_reply_markup(reply_markup=get_random_choice_game_settings_keyboard(settings_object, target_id, state_name))
    except:
        pass

    await callback.answer()


@random_choice_game_access_settings_router.message(RandomChoiceGameAccessSettingsStates.set_min_time, F.text.regexp(r"\d+"))
@random_choice_game_access_settings_router.message(RandomChoiceGameAccessSettingsStates.set_max_time, F.text.regexp(r"\d+"))
async def set_min_time(message: Message, member: ChatMember, state: FSMContext):
    state_data = await state.get_data()
    
    matches = re.findall(r"\d+", message.text)
    days, hours, minutes = (0,) * (3 - len(matches)) + tuple(map(int, matches))
    time = timedelta(days=days, hours=hours, minutes=minutes)

    time = max(time, timedelta(minutes=1))
    time = min(time, timedelta(days=365))

    data = await redis.get_deserialized(str(member.id))
    settings_object_id = uuid.UUID(data["dialogs"][str(state_data["message_id"])]["settings_object_id"])

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=settings_object_id)

    if await state.get_state() == RandomChoiceGameAccessSettingsStates.set_min_time:
        settings_object.min_punish_time_for_rand_choice = time
    elif await state.get_state() == RandomChoiceGameAccessSettingsStates.set_max_time:
        settings_object.max_punish_time_for_rand_choice = time

    await settings_object.asave()

    try:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=int(state_data["message_id"]),
            reply_markup=get_random_choice_game_settings_keyboard(settings_object, state_data["target_id"])
        )
    except:
        pass

    await message.delete()
    await state.clear()

