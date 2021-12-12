from aiogram import Bot
from aiogram.types import InlineKeyboardButton
import config
import logging
import markup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)


class Civilian:
    def __init__(self, user_profile):
        self.user_profile = user_profile
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


class Mafia(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 🤵🏼 Mafia!*\n"
                                                     "Your task is to obey Don and kill everyone who stands "
                                                     "in your way.", parse_mode="Markdown")


class Medic(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 👨🏼‍⚕️ Doctor!*\n"
                                                     "You decide who to save tonight ...",
                               parse_mode="Markdown")


class Police(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        await bot.send_message(self.user_profile.id, "*You are 🕵🏼‍♂️ Commissioner Cattani!*\n"
                                                     "The main city protector and the thunderstorm of "
                                                     "the mafia ...", parse_mode="Markdown")