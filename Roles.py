class Civilian:
    def __init__(self, user_id):
        self.user_id = user_id
        self.is_dead = False  # boolean is player alive or dead
        # self.is_mafia = False  # boolean is player mafia or not # We will use isinstance
        self.has_night_action = False  # boolean is role has night action or not
        self.priority = 0  # i'm not sure, int??

    def day(self, user_id):
        pass


class Mafia(Civilian):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.has_night_action = True
        self.priority = 1

    def night(self, info_for_chat):
        pass


class Medic(Civilian):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.has_night_action = True
        self.priority = 2

    def night(self, info_for_chat):
        pass


class Police(Civilian):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.has_night_action = True
        self.priority = 3

    def night(self, info_for_chat):
        pass

