from django.conf import settings
from django.utils.translation import gettext as _

base_dialog_text = "%(prefix)s" + "%(text)s"

punishment_creation_texts = {
    "name": "%(prefix)s" +
            _("To create a punishment, you need to write the name of the new punishment"),

    "time": "%(prefix)s" +
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

    "privacy": "%(prefix)s" +
               _("Now select the privacy of the new punishment"),
}

punishment_deletion_texts = {
    "select": "%(prefix)s" +
              _("Choose a punishment from the list below\n\n"
                "Category: %(category)s"),

    "accept": "%(prefix)s" +
              _("Accept deletion for %(punishment_name)s"),
}

random_choice_game_creation_texts = {
    "punishment": "%(prefix)s" +
                  _("Choose a punishment from the list below\n\n"
                    "Category: %(category)s"),

    "settings": "%(game_text)s"
}

random_choice_game_texts = {
    "game": "%(game_text)s\n\n"
            "%(game_players)s",

    "results": "%(game_losers)s"
}

access_settings_texts = {
    "target": _("Select target"),
    "base_settings": _("%(target_name)s"),
    "game_settings": _("%(target_name)s -> %(game_name)s"),
    "access_group": _("%(group_name)s\n\n"
                      "%(group_members)s\n\n"
                      "To add a user to a group, use one of these commands:\n"
                      "<code>/%(add_to_group_command)s %(group_id)s</code> (in response to a user message)\n"
                      "<code>/%(add_to_group_command)s %(group_id)s &lt;user_id or username&gt;</code>\n\n"
                      "You can remove a user from a group using the commands:\n"
                      "<code>/%(remove_from_group_command)s </code> (in response to a user message)\n"
                      "<code>/%(remove_from_group_command)s &lt;user_id or username&gt;</code>")
}

user_settings_texts = {
    "global": _("Global user settings (for local ones, go to the group chat of interest)"),
    "local": _("Local user settings (for global ones, go to private chat with the bot)")
}
