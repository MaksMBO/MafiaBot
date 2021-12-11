from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config
import logging
import markup
from aiogram.utils.callback_data import CallbackData

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)


class Civilian:
    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.is_dead = False  # boolean is player alive or dead
        self.another_player_id = 0
        self.button = 0

    def buttons(self, user):
        self.button = InlineKeyboardButton(
            f'{self.user_profile.first_name if self.user_profile.first_name else ""} '
            f'{self.user_profile.last_name if self.user_profile.last_name else ""}',
            callback_data=markup.cb.new(user_id=self.user_profile.id, button_for=user))

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are a 👨🏼 Civilian.*\n"
                                                     "Your task is to find the mafia and lynch the murderers "
                                                     "at the city meeting!", parse_mode="Markdown")

    def day(self, user_profile):
        pass


class Mafia(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 🤵🏼 Mafia!*\n"
                                                     "Your task is to obey Don and kill everyone who stands "
                                                     "in your way.", parse_mode="Markdown")

    async def night(self, info_for_chat):
        # написать пересылку сообщений, и кто кого убил
        pass


class Medic(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 👨🏼‍⚕️ Doctor!*\n"
                                                     "You decide who to save tonight ...",
                               parse_mode="Markdown")

    async def night(self, info_for_chat):
        pass


class Police(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 🕵🏼‍♂️ Commissioner Cattani!*\n"
                                                     "The main city protector and the thunderstorm of "
                                                     "the mafia ...", parse_mode="Markdown")

    async def night(self, info_for_chat):
        pass