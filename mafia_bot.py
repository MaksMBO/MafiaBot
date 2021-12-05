import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup
import json
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

MESSAGE_ID_NOTE = types.Message

is_registration = True
game = False
note = None


async def check_admin(chat_id, bot_id):
    bot_permission = await bot.get_chat_member(chat_id, bot_id)
    if bot_permission['status'] == "administrator" and bot_permission["can_manage_chat"] \
            and bot_permission["can_delete_messages"] and bot_permission["can_restrict_members"] \
            and bot_permission["can_manage_voice_chats"] and bot_permission["can_pin_messages"]:
        return True
    await bot.send_message(chat_id, """"Administrator rights have not been granted 
To start the game give me the following administrator rights: 
☑️ delete messages 
☑️ block users 
☑️ pin messages""")
    return False


async def update_data(users, user):
    if str(user.id) not in users:
        users[user.id] = {}
        users[user.id]['Games played'] = 0
        users[user.id]['Games won'] = 0


async def add_games_played(users, user, game_result):
    """add number of games that he played"""
    users[str(user.id)][game_result] += 1


players_joined = {}


@dp.message_handler(commands=['game'])
async def registration(message: types.Message):
    global is_registration
    if message.chat.id < 0 and is_registration and await check_admin(message.chat.id, bot.id):
        global players_joined
        await message.reply("Registration is open", reply_markup=markup.inline_keyboard_join)
        players_joined["chat_id"] = message.chat.id
        # players_joined["players_id"] = []
        # players_joined["players_name"] = []
        players_joined["players"] = []
        players_joined["time_remaining"] = 60
        is_registration = False

        information = {"chat_id": players_joined["chat_id"], "players": []}
        with open("registration.json", 'w') as file:
            json.dump(information, file, indent=4)

        await bot.send_message(message.chat.id, "Time until the end of registration 60 seconds")
        while players_joined["time_remaining"] > 0:
            players_joined["time_remaining"] -= 1
            if players_joined["time_remaining"] == 30:
                await bot.send_message(message.chat.id, "Time until the end of registration 30 seconds")
            await asyncio.sleep(1)
        await bot.send_message(message.chat.id, "Registration is over")
        global game
        game = True
        if len(players_joined["players"]) < 4:
            await bot.send_message(message.chat.id, "Not enough players to start the game...")
            players_joined.clear()
            is_registration = True


@dp.callback_query_handler(text="+30s")
async def timer_extend(call: types.CallbackQuery):
    if len(players_joined["players"]) > 1:
        players_joined["time_remaining"] += 30
        await bot.send_message(call.message.chat.id,
                               f"Added +30 seconds to the duration of registration. Time left till the game begins: "
                               f"{players_joined['time_remaining']}.")
    else:
        await bot.send_message(call.message.chat.id, "You need to have at least two registered users to extend the "
                                                     "timer")


@dp.message_handler(commands=['start'])
async def send_welcome_message(message: types.Message):
    if message.chat.id > 0:
        if message.get_args() == 'a':

            if players_joined["time_remaining"] == 0:
                await bot.send_message(message.from_user.id, "There is no game registered")
            elif message.from_user in players_joined["players"]:
                await bot.send_message(message.from_user.id,
                                       "You are already registered, just wait⌛️")
            else:
                await bot.send_message(message.from_user.id,
                                       "You have registered in the game, wait for the start✅")

                players_joined["players"].append(message.from_user)

                with open("registration.json", 'r') as file:
                    information = json.load(file)
                information["players"].append(dict(message.from_user))
                with open("registration.json", 'w') as file:
                    json.dump(information, file, indent=4)

                global note
                if len(players_joined["players"]) == 1:
                    note = await bot.send_message(players_joined["chat_id"],
                                                  "*Registration is in progress*\n\nRegistered:\n@" + "\n@".join(
                                                      map(str, (x.username for x in players_joined["players"]))))
                else:
                    await note.edit_text("*Registration is in progress*\n\nRegistered:\n@" + "\n@".join(
                        map(str, (x.username for x in players_joined["players"]))))
        else:
            await bot.send_message(message.from_user.id,
                                   "Hi! {0.first_name}, 🕴 I'm mafia bot ".format(message.from_user),
                                   reply_markup=markup.inline_keyboard_start)

        await message.delete()
    else:
        if await check_admin(message.chat.id, bot.id):
            if len(players_joined) == 0:
                error = await bot.send_message(message.chat.id, "Registration is not started now")
                await asyncio.sleep(5)
                await error.delete()

            elif len(players_joined["players"]) > 0:
                players_joined["time_remaining"] = 0
            else:
                error = await bot.send_message(message.chat.id, "A minimum of four users must be registered to stop"
                                                                " the timer")
                await asyncio.sleep(10)
                await error.delete()
            await message.delete()


@dp.callback_query_handler(text="Profile🤵🏻")
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
        call.from_user), reply_markup=markup.inline_keyboard_back, parse_mode="Markdown")


@dp.callback_query_handler(text="Help")
async def creating_buttons(call: types.CallbackQuery):
    await bot.send_message(call.from_user.id, "It`s help")


@dp.callback_query_handler(text="🔙")
async def creating_buttons(call: types.CallbackQuery):
    await call.message.delete()
    await bot.send_message(call.from_user.id,
                           "Hi! {0.first_name}, 🕴 I'm mafia bot ".format(call.from_user),
                           reply_markup=markup.inline_keyboard_start)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
