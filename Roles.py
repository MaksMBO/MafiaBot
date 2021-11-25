class Civilian:
    def __init__(self, user_id):
        self.user_id = user_id
        self.is_dead = False  # boolean is player alive or dead
        self.is_mafia = False  # boolean is player mafia or not
        self.has_night_action = False  # boolean is role has night action or not
        self.priority = 0  # i'm not sure, int??


class GunDon(Civilian):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.is_mafia = True
        self.has_night_action = True
        self.priority = 1


