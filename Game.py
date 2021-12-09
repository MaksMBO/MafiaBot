import random
import math

import markup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from Roles import Mafia, Police, Medic, Civilian
from aiogram import Bot, Dispatcher, executor, types
import config
import logging

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)


class Games:
    def __init__(self, players_info):
        self.players_info = players_info
        self.players_roles = {}
        self.game = True
        self.mafia_players = []
        self.civilian_players = []

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
        await bot.send_animation(self.players_info["chat_id"], gif, caption=f"*🏙 Day {day_counter}*\n"
                                                                            "The sun rises, drying the blood spilled"
                                                                            " at night on the sidewalks ..."
                                                                            " morning ...", parse_mode="Markdown")

    async def night(self):
        """

        role function run loop

        """
        gif = open('Other/sunset.gif', 'rb')
        await bot.send_animation(self.players_info["chat_id"], gif, caption="*🌃 Night falls*\n"
                                                                            "Only the most courageous and fearless "
                                                                            "take to the streets"
                                                                            " of the city. Let's try to count their "
                                                                            "heads in the"
                                                                            " morning ...",
                                 reply_markup=markup.inline_keyboard_bot, parse_mode="Markdown")
        for mafia in self.mafia_players:
            # self.button = InlineKeyboardButton(f'{self.user_profile.first_name} {self.user_profile.last_name}',
            #                                 callback_data=user_profile.id)
            keyboard = InlineKeyboardMarkup(row_width=1)
            for civilian in self.civilian_players:
                keyboard.add(civilian.button)
            await bot.send_message(mafia.user_profile.id, "*It's time to kill!*\nChoose a victim ", reply_markup=keyboard,
                                   parse_mode="Markdown")

    # написать в личку мафии, что наступила ночь, и оповестить его о его союзниках
    # for role in self.players_roles.values():
    #     if isinstance(role, Mafia):
    #         await bot.send_message(role.user_profile.id, "*You are 🤵🏼 Mafia!*\n"
    #                                                      "Your task is to obey Don and kill everyone who stands "
    #                                                      "in your way.", parse_mode="Markdown")
    #     elif isinstance(role, Police):
    #         await bot.send_message(role.user_profile.id, "*You are 🕵🏼‍♂️ Commissioner Cattani!*\n"
    #                                                      "The main city protector and the thunderstorm of "
    #                                                      "the mafia ...", parse_mode="Markdown")
    #     elif isinstance(role, Medic):
    #         await bot.send_message(role.user_profile.id, "*You are 👨🏼‍⚕️ Doctor!*\n"
    #                                                      "You decide who to save tonight ...",
    #                                parse_mode="Markdown")
    #     elif isinstance(role, Civilian):
    #         await bot.send_message(role.user_profile.id, "*You are a 👨🏼 Civilian.*\n"
    #                                                      "Your task is to find the mafia and lynch the murderers "
    #                                                      "at the city meeting!", parse_mode="Markdown")

    async def mafia_game(self):
        # if message.from_user.id not in self.players_roles.keys():
        #     await message.delete()
        for mafia in self.mafia_players:
            await bot.send_message(mafia.user_profile.id, "Remember your allies: \n@" + "\n@".join(
                map(str, (x.user_profile.username + "- 🤵🏼 Mafia" for x in self.mafia_players))))
        while self.game:
            await self.night()
            await self.day()
            self.game = False
