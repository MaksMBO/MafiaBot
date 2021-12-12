import random
import math
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import markup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from Roles import Mafia, Police, Medic, Civilian
from aiogram import Bot, Dispatcher, executor, types
import config
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Games:
    def __init__(self, players_info):
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
        self.lynching = 0
        self.message = 0
        self.role_dict = {}
        self.players_dict = {}

    async def give_roles(self):
        """
        Create a list with player id

        random roles

        create a dict(id is a key) with objects (roles)
        """

        i = 0  # ход раздачи
        ind = math.ceil(len(self.players_info["players"]) / 3) - 2  # количество дополнительных мафий
        while len(self.players_info["players"]) > 0:
            s = random.randint(0, len(self.players_info["players"]) - 1)
            if i <= ind:
                self.players_roles[self.players_info["players"][s]["id"]] = Mafia(self.players_info["players"][s])
            elif i == ind + 1:
                self.players_roles[self.players_info["players"][s]["id"]] = Police(self.players_info["players"][s])
            elif i == ind + 2:
                self.players_roles[self.players_info["players"][s]["id"]] = Medic(self.players_info["players"][s])
            else:
                self.players_roles[self.players_info["players"][s]["id"]] = Civilian(self.players_info["players"][s])
            self.players_info["players"].pop(s)
            i += 1
        for role in self.players_roles.values():
            await role.send_message()
            if isinstance(role, Mafia):
                self.mafia_players.append(role)
            else:
                self.civilian_players.append(role)

    async def day(self):
        """

        Start a timer for discussion
        voting in private messages
        if additional voting is needed, it is carried out in the general chat

        """

        day_counter = 1
        gif = open('Other/sunrise.gif', 'rb')
        await bot.send_animation(
            self.players_info["chat_id"], gif,
            caption=f"*🏙 Day {day_counter}*\nThe sun rises, drying the blood spilled at night on the sidewalks "
                    f"... morning ...", parse_mode="Markdown"
        )

        gif_kill = open('Other/Mafia_kill.gif', 'rb')
        gif_do_not_kill = open('Other/mafia_dont_kill.gif', 'rb')

        if self.night_kill:
            await bot.send_animation(
                self.players_info["chat_id"], gif_kill,
                caption=f'*{self.night_kill.user_profile.first_name if self.night_kill.user_profile.first_name else ""} '
                        f'{self.night_kill.user_profile.last_name if self.night_kill.user_profile.last_name else ""}* '
                        f'was killed that night',
                parse_mode="Markdown"
            )
        else:
            await bot.send_animation(
                self.players_info["chat_id"], gif_do_not_kill, caption=f'*No one was killed that night*',
                parse_mode="Markdown"
            )

        # тут время, которое даеться на принятие решения
        # выводит все кнопки в общий чат, для линчевания
        # await bot.send_message()
        keyboard_day = InlineKeyboardMarkup(row_width=1)
        for civilian in self.civilian_players:
            civilian.buttons("Day")
            keyboard_day.add(civilian.button)
        for mafia in self.mafia_players:
            mafia.buttons("Day")
            keyboard_day.add(mafia.button)
        await self.output_buttons_lynch(self.civilian_players, keyboard_day)
        await self.output_buttons_lynch(self.mafia_players, keyboard_day)
        self.end_night = False
        day_counter += 1

    @staticmethod
    async def check_lynching(dict_for_lynch):
        lynched_players = [player_id for player_id, counter_of_voices in dict_for_lynch.items() if
                           counter_of_voices == max(dict_for_lynch.values())]
        return lynched_players[0] if len(lynched_players) < 2 else None

    async def lynched(self):
        gif_none_lynched = open('Other/no_one_lynched.gif', 'rb')
        gif_lynching = open('Other/lynching.gif', 'rb')
        print(self.lynch)
        gif_direct_lynching = open('Other/lynched_message.gif', 'rb')

        lynch_dict = dict((lynch_id, self.lynch.count(lynch_id)) for lynch_id in self.lynch)
        person_lynched = await self.check_lynching(lynch_dict)
        print(f'BEFORE: {self.civilian_players} + {self.mafia_players}')
        if person_lynched:
            for civilian in self.civilian_players:
                if str(civilian.user_profile.id) == str(person_lynched):
                    await bot.send_animation(
                        self.players_info["chat_id"], gif_lynching,
                        caption=f'*@{civilian.user_profile.username} was lynched!*',
                        parse_mode="Markdown"
                    )
                    await bot.send_animation(civilian.user_profile.id, gif_direct_lynching, caption="You were lynched",
                                             parse_mode="Markdown")
                    self.civilian_players.remove(civilian)
            for mafia in self.mafia_players:
                if str(mafia.user_profile.id) == str(person_lynched):
                    await bot.send_animation(
                        self.players_info["chat_id"], gif_lynching,
                        caption=f'*@{mafia.user_profile.username} was lynched!*',
                        parse_mode="Markdown"
                    )
                    await bot.send_animation(mafia.user_profile.id, gif_direct_lynching, caption="You were lynched",
                                             parse_mode="Markdown")
                    self.mafia_players.remove(mafia)
            await self.end_game_check()
        else:
            await bot.send_animation(
                self.players_info["chat_id"], gif_none_lynched, caption=f'*Voices diverged.*\nNo one was lynched.',
                parse_mode="Markdown"
            )
        print(lynch_dict)
        lynch_dict.clear()
        self.lynch.clear()

    async def output_buttons_lynch(self, role, buttons):
        for person in role:
            self.message = await bot.send_message(
                person.user_profile.id, "*It's time to look for the guilty ones!*\nWho do you want to lynch?",
                reply_markup=buttons, parse_mode="Markdown"
            )
            self.players_dict[person.user_profile.id] = self.message

    async def night(self):
        """

        role function run loop

        """
        self.night_kill = 0
        gif = open('Other/sunset.gif', 'rb')
        await bot.send_animation(
            self.players_info["chat_id"], gif,
            caption="*🌃 Night falls*\nOnly the most courageous and fearless take to the streets of the city. "
                    "Let's try to count their heads in the morning ...",
            reply_markup=markup.inline_keyboard_bot, parse_mode="Markdown"
        )

        if str(self.doc_id) == self.doctor_heal:
            self.treat_yourself = True

        keyboard_doctor = InlineKeyboardMarkup(row_width=1)
        keyboard_cherif = InlineKeyboardMarkup(row_width=1)
        keyboard_mafia = InlineKeyboardMarkup(row_width=1)

        for civilian in self.civilian_players:
            civilian.buttons("Mafia")
            keyboard_mafia.add(civilian.button)

            if not isinstance(civilian, Police):
                civilian.buttons("Cherif")
                keyboard_cherif.add(civilian.button)

            if isinstance(civilian, Medic) and self.treat_yourself:
                continue
            if str(civilian.user_profile.id) != self.doctor_heal:
                civilian.buttons("Doctor")
                keyboard_doctor.add(civilian.button)

        for mafia in self.mafia_players:
            mafia.buttons("Cherif")
            keyboard_cherif.add(mafia.button)
            mafia.buttons("Doctor")
            keyboard_doctor.add(mafia.button)
            self.message_mafia = await bot.send_message(mafia.user_profile.id, "*It's time to kill!*\nChoose a victim ",
                                                        reply_markup=keyboard_mafia, parse_mode="Markdown")
            self.role_dict[mafia.user_profile.id] = self.message_mafia

        for civilian in self.civilian_players:
            if isinstance(civilian, Police):
                self.cherif_id = civilian.user_profile.id
                self.message_cherif = await bot.send_message(civilian.user_profile.id,
                                                             "*Choose who you want to check tonight.*\nChoose suspect:",
                                                             reply_markup=keyboard_cherif, parse_mode="Markdown")
                self.role_dict[civilian.user_profile.id] = self.message_cherif
            if isinstance(civilian, Medic):
                self.doc_id = civilian.user_profile.id
                self.message_doc = await bot.send_message(civilian.user_profile.id,
                                                          "*Who will you heal?*\nChoose a patient",
                                                          reply_markup=keyboard_doctor, parse_mode="Markdown")
                self.role_dict[civilian.user_profile.id] = self.message_doc

        # if str(self.doc_id) == self.doctor_heal:
        #     self.treat_yourself = True
        ##################################################################################################################

        self.kill_mafia = []
        self.doctor_heal = int(not any(self.doc_id == x.user_profile.id for x in self.civilian_players))
        self.cherif_check = int(not any(self.cherif_id == x.user_profile.id for x in self.civilian_players))
        self.end_night = True
        await self.end_game_check()

    async def end_game_check(self):
        gif_mafia_win = open("Other/victory_mafia.gif")
        gif_civilian_win = open("Other/victory_civilian.gif")
        if not self.mafia_players:
            await bot.send_animation(self.players_info["chat_id"], gif_civilian_win, caption="*Civilians won*\n",
                                     parse_mode="Markdown")
            self.game = False
        if len(self.mafia_players) == len(self.civilian_players):
            await bot.send_animation(self.players_info["chat_id"], gif_mafia_win, caption="*Civilians won*\n",
                                     parse_mode="Markdown")
            self.game = False

    async def mafia_kill(self):
        gif_direct_kill = open('Other/killed_ls.gif')
        dead = random.choice(self.kill_mafia)
        for civilian in self.civilian_players:
            if str(civilian.user_profile.id) == dead and not str(self.doctor_heal) == dead:
                await bot.send_animation(civilian.user_profile.id, gif_direct_kill, caption="*You were killed*",
                                         parse_mode="Markdown")
                self.civilian_players.remove(civilian)
                self.night_kill = civilian

        for mafia in self.mafia_players:
            if str(mafia.user_profile.id) == dead and not str(self.doctor_heal) == dead:
                await bot.send_animation(mafia.user_profile.id, gif_direct_kill, caption="*You were killed*",
                                         parse_mode="Markdown")
                self.mafia_players.remove(mafia)
                self.night_kill = mafia

    async def cherif_night(self):
        for mafia in self.mafia_players:
            if self.cherif_check == str(mafia.user_profile.id):
                await bot.send_message(self.cherif_id, f"The player {mafia.user_profile.username} is a mafia - 🤵🏼")
        for civilian in self.civilian_players:
            if self.cherif_check == str(civilian.user_profile.id):
                await bot.send_message(self.cherif_id,
                                       f"The player {civilian.user_profile.username} is not a mafia - 👨🏼")

    @staticmethod
    async def wait(mafia, doc, police):
        while len(mafia) == 0 or doc == 0 or police == 0:
            pass
        return mafia, doc, police

# прописать день(линчевание, таймер на линчевание),
# профиль игрока
