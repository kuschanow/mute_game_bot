from aiogram import Router
from aiogram.filters import invert_f
from aiogram.types import CallbackQuery
from django.utils.translation import gettext as _

from bot.filters import DialogAccessFilter

no_access_router = Router()


@no_access_router.callback_query(invert_f(DialogAccessFilter()))
async def no_access(callback: CallbackQuery):
    await callback.answer(_("You do not have access to this conversation"))
