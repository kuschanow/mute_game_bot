from aiogram_dialog_manager import DialogButton

from django.utils.translation import gettext as _


cancel = DialogButton("cancel", {"": _("Cancel")})

refuse = DialogButton("refuse", {"": _("Cancel")})

privacy = DialogButton("privacy",
                       {
                           "-1": _("Private Global"),
                           "0": _("Private Local"),
                           "1": _("Public")
                       },
                       lambda button_data: str(button_data["public_indicator"]))

accept = DialogButton("accept", {"": _("Accept")})

change_page = DialogButton("change_page",
                           {
                               "first": _("First"),
                               "prev": _("Previous"),
                               "next": _("Next"),
                               "last": _("Last")
                           },
                           lambda button_data: button_data["to_page"])

