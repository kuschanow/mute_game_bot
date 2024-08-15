from uuid import uuid4

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import Command, MagicData
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from django.conf import settings

from bot.models import User, Chat, ChatMember
from games.models import RandomChoiceGame, Punishment
from django.utils.translation import gettext as _

punishment_creation_router = Router()
punishment_creation_router.message.filter(MagicData(F.chat.type.is_not(ChatType.PRIVATE)))
punishment_creation_router.callback_query.filter(F.data.startswith("create_punish"))


@punishment_creation_router.message(Command(settings.CREATE_PUNISHMENT_COMMAND), F.from_user.id.in_(settings.ADMINS))
async def create_punishment_command(message: Message, user: User, chat: Chat, member: ChatMember, state: FSMContext):
    for i in range(25):
        await Punishment.objects.aget_or_create(name=f"test_{i}", created_by=member, is_public=True)



