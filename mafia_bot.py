import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup
import json
import time

from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
FIRST_PERSON = True
MESSAGE_ID_NOTE = types.Message


class My_states(StatesGroup):
    START = State()
    JOIN = State()
    PARTICIPANTS = State()


async def update_data(users, user):
    if str(user.id) not in users:
        users[user.id] = {}
        users[user.id]['Games played'] = 0
        users[user.id]['Games won'] = 0


async def add_games_played(users, user, game_result):
    """add number of games that he played"""
    users[str(user.id)][game_result] += 1


players_joined = {}


@dp.message_handler(commands=['game'], state="*")
async def send_invite(message: types.Message):
    if message.chat.id < 0:

        # if FIRST_PERSON:
        #     timing = time.time()
        #     id_person = message.from_user.id
        # if time.time() - timing > 60:
        await My_states.JOIN.set()
        await message.reply("Registration is open", reply_markup=markup.inline_keyboard_join)
        players_joined["chat_id"] = message.chat.id
        players_joined["players_id"] = []
        players_joined["players_name"] = []
    else:
        await bot.send_message(message.from_user.id, "a".format(message.from_user))


@dp.message_handler(commands=['start'], state='*')
async def send_welcome_message(message: types.Message):
    # await My_states.START.set()
    if message.chat.id > 0:
        if message.get_args() == 'a':

            if message.from_user.id in players_joined["players_id"]:
                await bot.send_message(message.from_user.id,
                                       "You are already registered, just wait⌛️")
            else:
                await bot.send_message(message.from_user.id,
                                       "You have registered in the game, wait for the start✅")

                players_joined["players_id"].append(message.from_user.id)
                print(players_joined["chat_id"])
                note = bot.send_message(players_joined["chat_id"], "\n".join(map(str, players_joined["players_id"])))
                await note
                # bot.edit_message_text(chat_id=players_joined["chat_id"], message_id=note.message_id)
            print(players_joined)

        else:
            await bot.send_message(message.from_user.id,
                                   "Hi! {0.first_name}, 🕴 I'm mafia bot ".format(message.from_user),
                                   reply_markup=markup.inline_keyboard_start)
            with open('users.json', 'r') as f:
                users = json.load(f)
            await update_data(users, message.from_user)
            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)
        await message.delete()
    else:
        await bot.send_message(message.from_user.id, "a".format(message.from_user))


@dp.callback_query_handler(text="qwe", state=My_states.JOIN)
async def creating_buttons(call: types.CallbackQuery):
    await My_states.JOIN.set()
    await bot.send_message(call.from_user.id, "Press JOIN to join the game".format(call.from_user),
                           reply_markup=markup.join_keyboard, parse_mode="Markdown")


@dp.callback_query_handler(text="Profile🤵🏻", state=My_states.START)
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
        call.from_user), reply_markup=markup.inline_keyboard_back, parse_mode="Markdown")


@dp.callback_query_handler(text="Help", state=My_states.START)
async def creating_buttons(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, "It`s help")


@dp.callback_query_handler(text="🔙", state=My_states.START)
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
        call.from_user), reply_markup=markup.inline_keyboard_start, parse_mode="Markdown")
    # await My_states.


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)