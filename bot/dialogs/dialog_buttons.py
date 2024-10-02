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
                          {
                              "normal": _("Min-Max players: %(min)d - %(max)s"),
                              "selected": _("▶ %(normal)s ◀")
                          },
                          lambda data: data["state"])

losers = ButtonPrototype("losers",
                         {
                             "normal": _("Losers count: %(losers)d"),
                             "selected": _("▶ %(normal)s ◀")
                         },
                         lambda data: data["state"])

autostart_when_full = ButtonPrototype("autostart_when_full",
                                      {"": _("Autostart when full %(indicator)s")},
                                      set_indicator)

create = ButtonPrototype("create", {"": _("Create")})

join = ButtonPrototype("join", {"": _("Join/Left")})

start = ButtonPrototype("start", {"": _("Start")})

delete = ButtonPrototype("delete", {"": _("Delete")})

stats_format = ButtonPrototype("stats_format",
                            {
                                "normal": _("%(format_name)s"),
                                "selected": _("▶ %(normal)s ◀")
                            },
                            lambda data: data["state"])

stats_category = ButtonPrototype("stats_category",
                            {
                                "normal": _("%(category_name)s"),
                                "selected": _("▶ %(normal)s ◀")
                            },
                            lambda data: data["state"])

settings_target = ButtonPrototype("settings_target",
                                  {
                                      "chat": _("Global"),
                                      "admins": _("Admins")
                                  },
                                  lambda data: data["target"])

make_diff = ButtonPrototype("make_diff", {"": _("Make different from global")})

back = ButtonPrototype("back", {"": _("Back")})

can_join_games = ButtonPrototype("can_join_games", {"": _("Can play %(status)s")})

can_create_games = ButtonPrototype("can_create_games", {"": _("Can create games %(status)s")})

can_press_other_buttons = ButtonPrototype("can_press_other_buttons", {"": _("Can press other buttons %(status)s")})

can_create_punishments = ButtonPrototype("can_create_punishments", {"": _("Can create punishments %(status)s")})

can_delete_punishments = ButtonPrototype("can_delete_punishments", {"": _("Can delete punishments %(status)s")})

is_invulnerable = ButtonPrototype("is_invulnerable", {"": _("Invulnerable %(status)s")})

hide_in_stats = ButtonPrototype("hide_in_stats", {"": _("Hide in stats %(status)s")})

games_settings = ButtonPrototype("games_settings", {"": _("Games settings")})

reset_to_global = ButtonPrototype("reset_to_global", {"": _("Reset to global")})

game_access_settings = ButtonPrototype("game_access_settings",
                                       {
                                           "random_choice_game": _("Random choice game")
                                       },
                                       lambda data: data["game"])

access_time_settings = ButtonPrototype("access_time_settings",
                                       {
                                           "min_time": _("Min time: %(time)s"),
                                           "max_time": _("Max time: %(time)s"),
                                           "min_time_selected": _("▶ %(min_time)s ◀"),
                                           "max_time_selected": _("▶ %(max_time)s ◀"),
                                       },
                                       lambda data: f"{data['type']}_{'selected' if data['selected'] else ''}".strip("_"))

ping_in_stats = ButtonPrototype("ping_in_stats", {"": _("Ping in stats %(status)s")})

add = ButtonPrototype("add", {"": _("Add")})

access_group = ButtonPrototype("access_group", {"": "%(name)s"})

update = ButtonPrototype("update", {"": _("Update")})
