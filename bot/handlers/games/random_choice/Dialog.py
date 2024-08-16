from typing import Dict, Any
from uuid import uuid4


class Dialog:
    def __init__(self):
        self.dialog_id = str(uuid4())
        self.punishment_menu_mapping = {}
        self.punishment_id = None

    def set_punishment_menu_mapping(self, punishment_menu_mapping: Dict[int, str]):
        self.punishment_menu_mapping = punishment_menu_mapping

    def select_punishment(self, index: int):
        self.punishment_id = self.punishment_menu_mapping[index]

    def to_dict(self):
        return {
            'dialog_id': self.dialog_id,
            'punishment_menu_mapping': self.punishment_menu_mapping,
            'punishment_id': self.punishment_id,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        dialog = Dialog()
        dialog.dialog_id = data['dialog_id']
        dialog.punishment_menu_mapping = {int(key): value for key, value in data['punishment_menu_mapping'].items()}
        dialog.punishment_id = data['punishment_id']
        return dialog
