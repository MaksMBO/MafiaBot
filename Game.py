from Imports import *
from Constants import *


class Games:
    """Class for creating game objects"""

    def __init__(self, players_info, number_game):
        """Constructor of the Game class
        :param players_info
        :param number_game

        """
        self.players_info = players_info
        self.players_roles = {}
        self.game = True
        self.mafia_players = []
        self.civilian_players = []
        self.kill_mafia = []
        self.doctor_heal = 0
        self.cherif_check = 0
        self.treat_yourself = False
        self.doc_id = 1
        self.cherif_id = 0
        self.end_night = False
        self.message_mafia = 0
        self.message_doc = 0
        self.message_cherif = 0
        self.night_kill = 0
        self.lynch = []
        self.message = 0
        self.role_dict = {}
        self.players_dict = {}
        self.day_counter = 0
        self.number_game = number_game

    async def give_roles(self):
        """Function for randomazing and giving roles for all players"""
        i = 0  # ход раздачи
        ind = math.ceil(
            len(self.players_info[self.players_info['chat_id']]["players"]) / 3) - 2  # количество дополнительных мафий
        while len(self.players_info[self.players_info['chat_id']]["players"]) > 0:
            s = random.randint(0, len(self.players_info[self.players_info['chat_id']]["players"]) - 1)
            if i <= ind:
                self.players_roles[self.players_info[self.players_info['chat_id']]["players"][s]["id"]] = Mafia(
                    self.players_info[self.players_info['chat_id']]["players"][s])
            elif i == ind + 1:
                self.players_roles[self.players_info[self.players_info['chat_id']]["players"][s]["id"]] = Police(
                    self.players_info[self.players_info['chat_id']]["players"][s])
            elif i == ind + 2:
                self.players_roles[self.players_info[self.players_info['chat_id']]["players"][s]["id"]] = Medic(
                    self.players_info[self.players_info['chat_id']]["players"][s])
            else:
                self.players_roles[self.players_info[self.players_info['chat_id']]["players"][s]["id"]] = Civilian(
                    self.players_info[self.players_info['chat_id']]["players"][s])
            self.players_info[self.players_info['chat_id']]["players"].pop(s)
            i += 1
        for role in self.players_roles.values():
            await role.send_message()
            if isinstance(role, Mafia):
                self.mafia_players.append(role)
            else:
                self.civilian_players.append(role)

    async def day(self):
        """
        Function for performance day actions
        """
        self.day_counter += 1
        gif_sunrise = open('Other/sunrise.gif', 'rb')
        await bot.send_animation(
            self.players_info["chat_id"], gif_sunrise,
            caption=f"*🏙 Day {self.day_counter}*\n" + DAY_START, parse_mode="Markdown"
        )
        gif_sunrise.close()


        if self.night_kill:
            gif_kill = open('Other/Mafia_kill.gif', 'rb')
            await bot.send_animation(
                self.players_info["chat_id"], gif_kill,
                caption=f'*{self.night_kill.user_profile.first_name if self.night_kill.user_profile.first_name else ""}'
                        f' {self.night_kill.user_profile.last_name if self.night_kill.user_profile.last_name else ""}* '
                        f'was killed that night',
                parse_mode="Markdown"
            )
            gif_kill.close()

        else:
            gif_do_not_kill = open('Other/mafia_dont_kill.gif', 'rb')
            await bot.send_animation(
                self.players_info["chat_id"], gif_do_not_kill, caption=NO_ONE_KILLED, parse_mode="Markdown"
            )
            gif_do_not_kill.close()

        keyboard_day = InlineKeyboardMarkup(row_width=1)
        for civilian in self.civilian_players:
            civilian.buttons("Day", self.number_game)
            keyboard_day.add(civilian.button)
        for mafia in self.mafia_players:
            mafia.buttons("Day", self.number_game)
            keyboard_day.add(mafia.button)
        await self.output_buttons_lynch(self.civilian_players, keyboard_day)
        await self.output_buttons_lynch(self.mafia_players, keyboard_day)
        self.end_night = False

    @staticmethod
    async def check_lynching(dict_for_lynch):
        """ the choice of who to lynch depending on the number of votes  """
        lynched_players = [player_id for player_id, counter_of_voices in dict_for_lynch.items() if
                           counter_of_voices == max(dict_for_lynch.values())]
        return lynched_players[0] if len(lynched_players) < 2 else None

    async def lynched(self):
        """ find and delete lynched person from game, send message to inform him and everyone, who was lynched """
        lynch_dict = dict((lynch_id, self.lynch.count(lynch_id)) for lynch_id in self.lynch)
        person_lynched = await self.check_lynching(lynch_dict)
        if person_lynched:
            for civilian in self.civilian_players:
                if str(civilian.user_profile.id) == str(person_lynched):
                    gif_lynching = open('Other/lynching.gif', 'rb')
                    await bot.send_animation(
                        self.players_info["chat_id"], gif_lynching,
                        caption=f'*@{civilian.user_profile.username} was lynched!*', parse_mode="Markdown"
                    )
                    gif_lynching.close()
                    gif_direct_lynching = open('Other/lynched_message.gif', 'rb')
                    await bot.send_animation(
                        civilian.user_profile.id, gif_direct_lynching, caption=YOU_LYNCHED, parse_mode="Markdown"
                    )
                    gif_direct_lynching.close()
                    self.civilian_players.remove(civilian)
            for mafia in self.mafia_players:
                if str(mafia.user_profile.id) == str(person_lynched):
                    gif_lynching = open('Other/lynching.gif', 'rb')
                    await bot.send_animation(
                        self.players_info["chat_id"], gif_lynching,
                        caption=f'*@{mafia.user_profile.username} was lynched!*', parse_mode="Markdown"
                    )
                    gif_lynching.close()
                    gif_direct_lynching = open('Other/lynched_message.gif', 'rb')
                    await bot.send_animation(
                        mafia.user_profile.id, gif_direct_lynching, caption=YOU_LYNCHED, parse_mode="Markdown"
                    )
                    gif_direct_lynching.close()
                    self.mafia_players.remove(mafia)
            await self.end_game_check()

        else:
            gif_none_lynched = open('Other/no_one_lynched.gif', 'rb')
            await bot.send_animation(
                self.players_info["chat_id"], gif_none_lynched, caption=DIVERSITY_STR, parse_mode="Markdown"
            )
            gif_none_lynched.close()
        lynch_dict.clear()
        self.lynch.clear()

    async def output_buttons_lynch(self, role, buttons):
        """ Displays a vote of who to lynch """
        for person in role:
            self.message = await bot.send_message(
                person.user_profile.id, LYNCHING, reply_markup=buttons, parse_mode="Markdown"
            )
            self.players_dict[person.user_profile.id] = self.message

    async def night(self):
        """
        Function for performing night actions
        """
        gif_sunset = open('Other/sunset.gif', 'rb')
        self.night_kill = 0
        await bot.send_animation(
            self.players_info["chat_id"], gif_sunset, caption=NIGHT_START,
            reply_markup=markup.inline_keyboard_bot, parse_mode="Markdown"
        )
        gif_sunset.close()

        if str(self.doc_id) == self.doctor_heal:
            self.treat_yourself = True

        keyboard_doctor = InlineKeyboardMarkup(row_width=1)
        keyboard_cherif = InlineKeyboardMarkup(row_width=1)
        keyboard_mafia = InlineKeyboardMarkup(row_width=1)

        for civilian in self.civilian_players:
            civilian.buttons("Mafia", self.number_game)
            keyboard_mafia.add(civilian.button)

            if not isinstance(civilian, Police):
                civilian.buttons("Cherif", self.number_game)
                keyboard_cherif.add(civilian.button)

            if isinstance(civilian, Medic) and self.treat_yourself:
                continue
            if str(civilian.user_profile.id) != self.doctor_heal:
                civilian.buttons("Doctor", self.number_game)
                keyboard_doctor.add(civilian.button)

        for mafia in self.mafia_players:
            mafia.buttons("Cherif", self.number_game)
            keyboard_cherif.add(mafia.button)
            mafia.buttons("Doctor", self.number_game)
            keyboard_doctor.add(mafia.button)
            self.message_mafia = await bot.send_message(
                mafia.user_profile.id, MAFIA_KILL_STR, reply_markup=keyboard_mafia, parse_mode="Markdown"
            )
            self.role_dict[mafia.user_profile.id] = self.message_mafia

        for civilian in self.civilian_players:
            if isinstance(civilian, Police):
                self.cherif_id = civilian.user_profile.id
                self.message_cherif = await bot.send_message(
                    civilian.user_profile.id, POLICE_CHECK_STR, reply_markup=keyboard_cherif, parse_mode="Markdown"
                )
                self.role_dict[civilian.user_profile.id] = self.message_cherif
            if isinstance(civilian, Medic):
                self.doc_id = civilian.user_profile.id
                self.message_doc = await bot.send_message(
                    civilian.user_profile.id, MEDIC_HEAL_STR, reply_markup=keyboard_doctor, parse_mode="Markdown"
                )
                self.role_dict[civilian.user_profile.id] = self.message_doc

        self.kill_mafia = []

        # Should convert to bool #######################################################################################
        self.doctor_heal = int(not any(self.doc_id == x.user_profile.id for x in self.civilian_players))
        self.cherif_check = int(not any(self.cherif_id == x.user_profile.id for x in self.civilian_players))
        self.end_night = True
        await self.end_game_check()

    @staticmethod
    async def add_win(list_of_winners):
        """ function to add win in profile of winner """
        with open('users.json', 'r') as f:
            users = json.load(f)
            for user in list_of_winners:
                users[str(user.user_profile.id)]['Games won'] += 1
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

    async def end_game_check(self):
        """ Function for checking if the game is over """
        if not self.mafia_players:
            await bot.send_message(self.players_info["chat_id"], CIVILIANS_WON_STR, parse_mode="Markdown")
            await self.add_win(self.civilian_players)
            self.game = False
        if len(self.mafia_players) == len(self.civilian_players):
            await bot.send_message(self.players_info["chat_id"], MAFIA_WON_STR, parse_mode="Markdown")
            await self.add_win(self.mafia_players)
            self.game = False

    async def mafia_kill(self):
        """ Function that checks whether the mafia has killed
        the player or not, depending on whether the doctor
        has treated the player chosen by the mafia """
        dead = random.choice(self.kill_mafia)
        for civilian in self.civilian_players:
            if str(civilian.user_profile.id) == dead and not str(self.doctor_heal) == dead:
                await bot.send_message(civilian.user_profile.id, YOU_KILLED, parse_mode="Markdown")
                self.civilian_players.remove(civilian)
                self.night_kill = civilian
                await self.end_game_check()

        for mafia in self.mafia_players:
            if str(mafia.user_profile.id) == dead and not str(self.doctor_heal) == dead:
                await bot.send_message(mafia.user_profile.id, YOU_KILLED, parse_mode="Markdown")
                self.mafia_players.remove(mafia)
                self.night_kill = mafia
                await self.end_game_check()

    async def cherif_night(self):
        """ Function that tells the mafia sheriff whether the player he has chosen for checking or not """
        for mafia in self.mafia_players:
            if self.cherif_check == str(mafia.user_profile.id):
                await bot.send_message(
                    self.cherif_id, f"The player {mafia.user_profile.username} is a mafia - 🤵🏼"
                )
        for civilian in self.civilian_players:
            if self.cherif_check == str(civilian.user_profile.id):
                await bot.send_message(
                    self.cherif_id, f"The player {civilian.user_profile.username} is not a mafia - 👨🏼"
                )

    @staticmethod
    async def wait(mafia, doc, police):
        """ function that checks if everyone voted at night """
        while len(mafia) == 0 or doc == 0 or police == 0:
            pass
        return mafia, doc, police

    def __str__(self):
        return str(self.__dict__)
