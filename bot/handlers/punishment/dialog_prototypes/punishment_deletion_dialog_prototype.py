from aiogram_dialog_manager import DialogPrototype
from django.utils.translation import gettext as _
from bot.dialog_buttons import cancel, privacy, punishment, accept, change_page, refuse

texts = {
    "punishment_select": "%(prefix)s" +
                         _("Choose a punishment from the list below\n\n"
                         "Category: %(category)s"),

    "accept": "%(prefix)s" +
              _("Accept deletion for %(punishment_name)s"),
}

punishment_deletion = DialogPrototype(type_name="punishment_deletion",
                                      texts=texts,
                                      buttons=[cancel, punishment, accept, change_page, privacy, refuse])
