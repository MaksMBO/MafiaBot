import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup
import json

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


async def update_data(users, user):
    if str(user.id) not in users:
        users[user.id] = {}
        users[user.id]['Games played'] = 0
        users[user.id]['Games won'] = 0


async def add_games_played(users, user, game_result):
    """add number of games that he played"""
    users[str(user.id)][game_result] += 1


@dp.message_handler(commands=['game'])
async def send_invite(message: types.Message):
    await message.reply("Registration is open", reply_markup=markup.inline_keyboard_join)


@dp.message_handler(commands=['start'])
async def send_welcome_message(message: types.Message):
    await bot.send_message(message.from_user.id, "Hi! {0.first_name}, 🕴️ I'm mafia bot ".format(message.from_user),
                           reply_markup=markup.inline_keyboard_start)
    with open('users.json', 'r') as f:
        users = json.load(f)
    await update_data(users, message.from_user)
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)


@dp.callback_query_handler(text="Profile🤵🏻")
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
        call.from_user), reply_markup=markup.inline_keyboard_back, parse_mode="Markdown")


@dp.callback_query_handler(text="Help")
async def creating_buttons(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, "jhu")


@dp.callback_query_handler(text="🔙")
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
        call.from_user), reply_markup=markup.inline_keyboard_start, parse_mode="Markdown")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
