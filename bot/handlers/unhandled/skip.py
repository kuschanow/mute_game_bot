from aiogram import Router, F
from aiogram.types import CallbackQuery
from django.utils.translation import gettext as _

skip_router = Router()
skip_router.callback_query.filter(F.data == "skip")


@skip_router.callback_query()
async def no_access(callback: CallbackQuery):
    await callback.answer()
