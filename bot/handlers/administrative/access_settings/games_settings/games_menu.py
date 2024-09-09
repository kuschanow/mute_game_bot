import uuid

from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.filters import IsOwner
from bot.handlers.administrative.access_settings.utils.access_settings_keyboards import get_random_choice_game_settings_keyboard
from bot.models import AccessSettingsObject, ChatMember
from shared import target, redis
from django.utils.translation import gettext as _

games_menu_router = Router()
games_menu_router.callback_query.filter(F.data.startswith("stgs:games_menu"), IsOwner())


@games_menu_router.callback_query(F.data.contains("rcg"))
async def random_choice_game(callback: CallbackQuery, member: ChatMember):
    data = await redis.get_deserialized(str(member.id))
    settings_object_id = uuid.UUID(data["dialogs"][str(callback.message.message_id)]["settings_object_id"])
    target_id = callback.data.split(":")[2]

    settings_object: AccessSettingsObject = await AccessSettingsObject.objects.aget(id=settings_object_id)

    try:
        await callback.message.edit_text(text=_("%(target)s -> Random choice game") % {"target": target[target_id]},
                                         reply_markup=get_random_choice_game_settings_keyboard(settings_object, target_id))
    except:
        pass
    await callback.answer()


