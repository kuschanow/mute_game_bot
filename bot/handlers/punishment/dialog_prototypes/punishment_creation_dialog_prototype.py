from aiogram_dialog_manager import DialogPrototype
from django.utils.translation import gettext as _
from bot.dialog_buttons import cancel, privacy

texts = {
    "punishment_name": "%(prefix)s" +
                       _("To create a punishment, you need to write the name of the new punishment"),

    "punishment_time": "%(prefix)s" +
                       _("Name: %(name)s\n\n"
                         "Now send the time of punishment\n\n") +
                       _("Time can be specified in any of the following ways:") +
                       _("<blockquote>"
                         "5:30 – 5 hours and 30 minutes\n"
                         "30 – 30 minutes\n"
                         "5 30 – the same as first\n"
                         "1:0:0 – 1 day\n"
                         "1 5 0 – 1 day and 5 hours\n"
                         "40:00 – 40 hours\n"
                         "100 – 100 minutes"
                         "</blockquote>"),

    "punishment_privacy": "%(prefix)s" +
                          _("Now select the privacy of the new punishment"),
}

punishment_creation = DialogPrototype(type_name="punishment_creation",
                            texts=texts,
                            buttons=[cancel, privacy],
                            get_state_from_reply=True)
