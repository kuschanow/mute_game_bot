from aiogram_dialog_manager import DialogPrototype
from django.utils.translation import gettext as _
from bot.dialog_buttons import cancel, privacy, punishment, change_page, is_creator_play, min_max, losers, autostart_when_full, create

texts = {
    "punishment": "%(prefix)s" +
                  _("Choose a punishment from the list below\n\n"
                    "Category: %(category)s"),

    "settings": "%(game_text)s"
}

game_creation = DialogPrototype(type_name="game_creation",
                            texts=texts,
                            buttons=[cancel, privacy, punishment, change_page, is_creator_play, min_max, losers, autostart_when_full, create],
                            get_state_from_reply=True)
