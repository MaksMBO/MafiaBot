import json
import random
import math
from Roles import Mafia, Police, Medic, Civilian
from mafia_bot import players_joined


class Game:
    def give_roles(self):
        """
        Create a list with player id

        random roles

        create a dict(id is a key) with objects (roles)
        """

        d = {}
        with open("registration.json", 'r') as file:
            list1 = json.load(file)["players"]

        i = 0  # ход раздачи
        ind = math.ceil(len(list1) / 3) - 2  # количество дополнительных мафий
        while len(list1) > 0:
            s = random.randint(0, len(list1) - 1)
            if i <= ind:
                d[list1[s]["id"]] = Mafia(list1[s])
            elif i == ind + 1:
                d[list1[s]["id"]] = Police(list1[s])
            elif i == ind + 2:
                d[list1[s]["id"]] = Medic(list1[s])
            else:
                d[list1[s]["id"]] = Civilian(list1[s])
            list1.pop(s)
            i += 1
        print(d)

    def day(self):
        """

        Start a timer for discussion

        voting in private messages

        if additional voting is needed, it is carried out in the general chat

        """

        pass

    def night(self):
        """

        role function run loop

        """
        pass

    def game(self):
        while True:
            self.night()
            self.day()


if __name__ == '__main__':
    Game().give_roles()
