class Civilian:
    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.is_dead = False  # boolean is player alive or dead
        # self.is_mafia = False  # boolean is player mafia or not # We will use isinstance
        self.has_night_action = False  # boolean is role has night action or not
        self.another_player_id = 0

    def day(self, user_profile):
        pass


class Mafia(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)
        self.has_night_action = True

    async def night(self, info_for_chat):
        # написать пересылку сообщений, и кто кого убил
        pass


class Medic(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)
        self.has_night_action = True

    async def night(self, info_for_chat):
        pass


class Police(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)
        self.has_night_action = True

    async def night(self, info_for_chat):
        pass