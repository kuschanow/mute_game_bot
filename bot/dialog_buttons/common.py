from aiogram_dialog_manager import DialogButton

from django.utils.translation import gettext as _


cancel = DialogButton("cancel", {"": _("Cancel")})

privacy = DialogButton("privacy",
                       {
                           "-1": _("Private Global"),
                           "0": _("Private Local"),
                           "1": _("Public")
                       },
                       lambda button_data: str(button_data["public_indicator"])
)

