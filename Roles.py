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

    def buttons(self, user, number):
        self.button = InlineKeyboardButton(
            f'{self.user_profile.first_name if self.user_profile.first_name else ""} '
            f'{self.user_profile.last_name if self.user_profile.last_name else ""}',
            callback_data=markup.cb.new(user_id=self.user_profile.id, button_for=user, id_game=number))

    async def send_message(self):
        """ Sends a message to the civilians to inform them of their role """
        await bot.send_message(self.user_profile.id, "<b>You are a 👨🏼 Civilian.</b>\n"
                                                     "Your task is to find the mafia and lynch the murderers "
                                                     "at the city meeting!", parse_mode="HTML")


class Mafia(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        """ Sends a message to the mafia to inform them of their role """
        await bot.send_message(self.user_profile.id, "<b>You are 🤵🏼 Mafia!</b>\n"
                                                     "Your task is to obey Don and kill everyone who stands "
                                                     "in your way.", parse_mode="HTML")


class Medic(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        """ Sends a message to the Doctor to inform him of his role """
        await bot.send_message(self.user_profile.id, "<b>You are 👨🏼‍⚕️ Doctor!</b>\n"
                                                     "You decide who to save tonight ...",
                               parse_mode="HTML")


class Police(Civilian):
    def __init__(self, user_profile):
        super().__init__(user_profile)

    async def send_message(self):
        """ Sends a message to the Commissioner Cattani to inform him of his role """
        await bot.send_message(self.user_profile.id, "<b>You are 🕵🏼‍♂️ Commissioner Cattani!</b>\n"
                                                     "The main city protector and the thunderstorm of "
                                                     "the mafia ...", parse_mode="HTML")