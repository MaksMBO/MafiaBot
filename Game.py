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

        medic = 0
        police = 0
        keyboard_players = InlineKeyboardMarkup(row_width=1)
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard_for_police = InlineKeyboardMarkup(row_width=1)
        for civilian in self.civilian_players:
            keyboard.add(civilian.button)
            keyboard_players.add(civilian.button)
            if isinstance(civilian, Medic):
                medic = civilian
            if not isinstance(civilian, Police):
                keyboard_for_police.add(civilian.button)
            else:
                police = civilian
        for mafia in self.mafia_players:
            keyboard_players.add(mafia.button)
            keyboard_for_police.add(mafia.button)
            await bot.send_message(mafia.user_profile.id, "*It's time to kill!*\nChoose a victim ",
                                   reply_markup=keyboard, parse_mode="Markdown")
        await bot.send_message(medic.user_profile.id, "*Who will you heal?*\nChoose a patient",
                               reply_markup=keyboard_players, parse_mode="Markdown")
        await bot.send_message(police.user_profile.id, "*Choose who you want to check tonight.*\nChoose suspect:",
                               reply_markup=keyboard_for_police, parse_mode="Markdown")

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
