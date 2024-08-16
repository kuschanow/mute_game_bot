from aiogram import Router

from .user_middlewares import set_user_middlewares
from .chat_middlewares import set_chat_middlewares
from .member_middlewares import set_member_middlewares
from .dialog_middlewares import set_dialog_middlewares

def set_middlewares(router: Router):
    set_user_middlewares(router)
    set_chat_middlewares(router)
    set_member_middlewares(router)
