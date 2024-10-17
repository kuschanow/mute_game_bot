from aiogram_dialog_manager.prototype import MenuPrototype

from .dialog_buttons import cancel as cancel_button, privacy as privacy_button, accept as accept_button, refuse, \
    settings_target as settings_target_button, game_access_settings, back, delete, update
from .keyboards import get_punishments_keyboard, get_stats_keyboard
from .keyboards.chat_settings.access_group_selection import get_access_group_selection_keyboard
from .keyboards.random_choice_game import get_settings_keyboard as get_random_choice_game_settings_keyboard, get_game_menu_keyboard as get_random_choice_game_menu_keyboard
from .keyboards.chat_settings.access_settings import get_access_settings_keyboard
from .keyboards.chat_settings.random_choice_game_access_settings import get_random_choice_game_access_settings_keyboard
from .keyboards.user_settings import get_user_settings

cancel = MenuPrototype(lambda: [[cancel_button.get_instance()]])

privacy = MenuPrototype(lambda settings: [
    [privacy_button.get_instance({"public_indicator": -1}), privacy_button.get_instance({"public_indicator": 0})],
    [privacy_button.get_instance({"public_indicator": 1})] if settings.can_create_public_punishments else [],
    [cancel_button.get_instance()]
])

punishments = MenuPrototype(get_punishments_keyboard)

accept = MenuPrototype(lambda p_id: [[accept_button.get_instance({"id": p_id})], [refuse.get_instance()]])

random_choice_settings = MenuPrototype(get_random_choice_game_settings_keyboard)

random_choice_game = MenuPrototype(get_random_choice_game_menu_keyboard)

stats = MenuPrototype(get_stats_keyboard)

settings_target = MenuPrototype(lambda is_super_admin: [
    [settings_target_button.get_instance({"target": "super_admin"})] if is_super_admin else []
    [settings_target_button.get_instance({"target": "owner"})]
    [settings_target_button.get_instance({"target": "chat"})],
    [settings_target_button.get_instance({"target": "admins"})],
    [settings_target_button.get_instance({"target": "group"})],
])

access_settings = MenuPrototype(get_access_settings_keyboard)

game_settings_select = MenuPrototype(lambda: [
    [game_access_settings.get_instance({"game": "random_choice_game"})],
    [back.get_instance({"page": "main_settings"})]
])

random_choice_game_access_settings = MenuPrototype(get_random_choice_game_access_settings_keyboard)

user_settings = MenuPrototype(get_user_settings)

access_groups = MenuPrototype(get_access_group_selection_keyboard)

access_group = MenuPrototype(lambda: [
    [update.get_instance({"page": "access_group"})]
    [delete.get_instance()],
    [back.get_instance({"page": "access_groups"})]
    [cancel_button.get_instance()],
])

