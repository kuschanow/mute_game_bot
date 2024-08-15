from games.models import Punishment


class PunishmentService:
    def __init__(self, instance: Punishment):
        self.instance = instance

