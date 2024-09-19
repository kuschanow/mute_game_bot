from typing import Any, Dict

from aiogram_dialog_manager import DialogButton

from django.utils.translation import gettext as _


def set_indicator(button_data: Dict[str, Any]):
    button_data["indicator"] = '✅' if button_data["value"] else '☑️'
    return ""

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

punishment = DialogButton("punishment", {"": "%(name)s"})

is_creator_play = DialogButton("is_creator_play",
                               {"": _("Add creator as player %(indicator)s")},
                               set_indicator)

min_max = DialogButton("min_max",
                       {"normal": _("Min-Max players: %(min)d - %(max)s"),
                        "selected": _("▶ %(normal)s ◀")},
                       lambda button_data: button_data["state"])

losers = DialogButton("losers",
                       {"normal": _("Losers count: %(losers)d"),
                        "selected": _("▶ %(normal)s ◀")},
                       lambda button_data: button_data["state"])

autostart_when_full = DialogButton("autostart_when_full",
                                   {"": _("Autostart when full %(indicator)s")},
                                   set_indicator)

create = DialogButton("create", {"": _("Create")})

join = DialogButton("join", {"": _("Join/Left")})

start = DialogButton("start", {"": _("Start")})

delete = DialogButton("delete", {"": _("Delete")})
