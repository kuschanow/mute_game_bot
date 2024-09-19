from aiogram_dialog_manager import DialogPrototype

from bot.dialog_buttons import delete, start, join

texts = {
    "game": "%(game_text)s\n\n"
            "%(game_players)s",
    
    "results": "%(game_losers)s"
}

game_dialog = DialogPrototype(type_name="game_dialog",
                            texts=texts,
                            buttons=[delete, start, join],
                            get_state_from_reply=True)
