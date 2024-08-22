from aiogram import Router
from aiogram.filters import invert_f
from aiogram.types import CallbackQuery
from django.utils.translation import gettext as _

from bot.filters import DialogAccess, IsGameCreator

no_access_router = Router()


@no_access_router.callback_query(invert_f(DialogAccess()))
async def no_access_to_dialog(callback: CallbackQuery):
    await callback.answer(_("You do not have access to this conversation"))


@no_access_router.callback_query(invert_f(IsGameCreator()))
async def no_access_to_action(callback: CallbackQuery):
    await callback.answer(_("You can't do this"))

