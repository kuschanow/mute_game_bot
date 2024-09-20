from typing import Any, Dict

from aiogram_dialog_manager.prototype import ButtonPrototype
from django.utils.translation import gettext as _


def set_indicator(data: Dict[str, Any]):
    data["indicator"] = '✅' if data["value"] else '☑️'
    return ""


cancel = ButtonPrototype("cancel", {"": _("Cancel")})

refuse = ButtonPrototype("refuse", {"": _("Cancel")})

privacy = ButtonPrototype("privacy",
                          {
                              "-1": _("Private Global"),
                              "0": _("Private Local"),
                              "1": _("Public")
                          },
                          lambda data: str(data["public_indicator"]))

accept = ButtonPrototype("accept", {"": _("Accept")})

change_page = ButtonPrototype("change_page",
                              {
                                  "first": _("First"),
                                  "prev": _("Previous"),
                                  "next": _("Next"),
                                  "last": _("Last")
                              },
                              lambda data: data["to_page"])

punishment = ButtonPrototype("punishment", {"": "%(name)s"})

is_creator_play = ButtonPrototype("is_creator_play",
                                  {"": _("Add creator as player %(indicator)s")},
                                  set_indicator)

min_max = ButtonPrototype("min_max",
                          {"normal": _("Min-Max players: %(min)d - %(max)s"),
                           "selected": _("▶ %(normal)s ◀")},
                          lambda data: data["state"])

losers = ButtonPrototype("losers",
                         {"normal": _("Losers count: %(losers)d"),
                          "selected": _("▶ %(normal)s ◀")},
                         lambda data: data["state"])

autostart_when_full = ButtonPrototype("autostart_when_full",
                                      {"": _("Autostart when full %(indicator)s")},
                                      set_indicator)

create = ButtonPrototype("create", {"": _("Create")})

join = ButtonPrototype("join", {"": _("Join/Left")})

start = ButtonPrototype("start", {"": _("Start")})

delete = ButtonPrototype("delete", {"": _("Delete")})
