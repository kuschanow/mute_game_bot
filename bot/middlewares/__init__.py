from aiogram import Router

from .chat_middlewares import set_chat_middlewares
from .logger_middlewares import set_logger_middlewares
from .member_middlewares import set_member_middlewares
from .random_choice_game_middleware import set_random_choice_game_middlewares
from .restricted_users_middleware import set_restricted_user_middlewares
from .settings_middlewares import set_settings_middlewares
from .user_middlewares import set_user_middlewares


def set_middlewares(router: Router):
    set_restricted_user_middlewares(router)
    set_user_middlewares(router)
    set_chat_middlewares(router)
    set_member_middlewares(router)
    set_settings_middlewares(router)
    #set_logger_middlewares(router)
