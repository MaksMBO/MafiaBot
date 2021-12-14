from aiogram.types import update

import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup
import json
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from Game import Games

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

MESSAGE_ID_NOTE = types.Message

is_registration = True
note = None
game = True
save_game = MemoryStorage()
number_of_game_id = 0


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
game_number = {}


@dp.message_handler(commands=['game'])
async def registration(message: types.Message):
    global is_registration
    global number_of_game_id
    number_of_game_id += 1
    if message.chat.id < 0 and is_registration and await check_admin(message.chat.id, bot.id):
        global players_joined
        await message.reply("Registration is open", reply_markup=markup.inline_keyboard_join)
        players_joined["chat_id"] = message.chat.id
        players_joined["players"] = []
        players_joined["time_remaining"] = 60
        is_registration = False

        await bot.send_message(message.chat.id, "Time until the end of registration 60 seconds")
        while players_joined["time_remaining"] > 0:
            players_joined["time_remaining"] -= 1
            if players_joined["time_remaining"] == 30:
                await bot.send_message(message.chat.id, "Time until the end of registration 30 seconds")
            if len(players_joined["players"]) >= 13:
                players_joined["time_remaining"] = 0
            await asyncio.sleep(1)
        await bot.send_message(message.chat.id, "Registration is over")
        if len(players_joined["players"]) < 4:
            await bot.send_message(message.chat.id, "Not enough players to start the game...")
            players_joined.clear()
            is_registration = True
        else:
            await bot.send_message(message.chat.id, "*GAME IS STARTED*", parse_mode="Markdown")
            game_number[str(number_of_game_id)] = Games(players_joined, number_of_game_id)
            if message.from_user not in players_joined["players"]:
                await message.delete()
            await game_number[str(number_of_game_id)].give_roles()
            # вот почему у нас другие задаются Макс, тут проблема походу в инициализации....
            for mafia in game_number[str(number_of_game_id)].mafia_players:
                await bot.send_message(mafia.user_profile.id, "Remember your allies: \n@" + "\n@".join(
                    map(str, (x.user_profile.username + "- 🤵🏼 Mafia" for x in
                              game_number[str(number_of_game_id)].mafia_players))))

            while game_number[str(number_of_game_id)].game:
                # if not this_game.end_night:
                await game_number[str(number_of_game_id)].night()

                await handlers_call(game_number[str(number_of_game_id)])
                while len(game_number[str(number_of_game_id)].kill_mafia) == 0 or \
                        game_number[str(number_of_game_id)].doctor_heal == 0 or \
                        game_number[str(number_of_game_id)].cherif_check == 0:
                    await asyncio.sleep(1)
                await game_number[str(number_of_game_id)].mafia_kill()
                await game_number[str(number_of_game_id)].cherif_night()
                await game_number[str(number_of_game_id)].day()
                timer = 120
                while len(game_number[str(number_of_game_id)].lynch) < len(
                        game_number[str(number_of_game_id)].civilian_players) + len(
                        game_number[str(number_of_game_id)].mafia_players) and timer >= 0:
                    if timer == 60:
                        await bot.send_message(players_joined["chat_id"], "One minute remaining")
                    if timer == 30:
                        await bot.send_message(players_joined["chat_id"], "30 seconds remaining")
                    await asyncio.sleep(1)
                    timer -= 1
                await game_number[str(number_of_game_id)].lynched()
            is_registration = True


async def handlers_call(games):
    print(f"Тык - {games}")

    @dp.message_handler(lambda mes: (str(mes.from_user.id) not in
                                     map(str, (x.user_profile.id for x in games.civilian_players + games.mafia_players))
                                     or games.end_night) and games.game)
    async def chat_moderating(mes: types.Message):
        await mes.delete()

    @dp.callback_query_handler(markup.cb.filter(button_for="Mafia"))
    async def callbacks_mafia(call: types.CallbackQuery, callback_data: dict):
        # games.kill_mafia.append(callback_data['user_id'])
        print(game_number)
        game_number[callback_data['id_game']].kill_mafia.append(callback_data['user_id'])
        print(f'{games.role_dict}\n\n\n\n\n\n\n\n\n')
        print(f"Game {games}")
        await editing_message(game_number[callback_data['id_game']], callback_data, game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*Mafia loaded weapons*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Doctor"))
    async def callbacks_doctor(call: types.CallbackQuery, callback_data: dict):
        game_number[callback_data['id_game']].doctor_heal = callback_data['user_id']
        print(f'{games.role_dict}\n\n\n\n\n\n\n\n\n')
        print(f"Game {games}")
        await editing_message(game_number[callback_data['id_game']], callback_data, game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*The doctor went out on night duty*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Cherif"))
    async def callbacks_cherif(call: types.CallbackQuery, callback_data: dict):
        game_number[callback_data['id_game']].cherif_check = callback_data['user_id']
        print(f'{games.role_dict}\n\n\n\n\n\n\n\n\n')
        print(f"Game {games}")
        await editing_message(game_number[callback_data['id_game']], callback_data, game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*The Commissioner went to look for the guilty*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Day"))
    async def callbacks_day(call: types.CallbackQuery, callback_data: dict):
        game_number[callback_data['id_game']].lynch.append(callback_data['user_id'])
        await editing_message(game_number[callback_data['id_game']], callback_data, game_number[callback_data['id_game']].players_dict[call.from_user.id])


async def editing_message(games, callback_data, dicts):
    for civilian in games.civilian_players:
        if str(callback_data['user_id']) == str(civilian.user_profile.id):
            await dicts.edit_text(f"You have chosen a {civilian.user_profile.username}")
    for mafia in games.mafia_players:
        if str(callback_data['user_id']) == str(mafia.user_profile.id):
            await dicts.edit_text(f"You have chosen a {mafia.user_profile.username}")


@dp.callback_query_handler(text="+30s")
async def timer_extend(call: types.CallbackQuery):
    if len(players_joined["players"]) > 1:
        players_joined["time_remaining"] += 30
        await bot.send_message(
            call.message.chat.id, f"Added +30 seconds to the duration of registration. Time left till the game begins: "
                                  f"{players_joined['time_remaining']}."
        )
    else:
        await bot.send_message(
            call.message.chat.id, "You need to have at least two registered users to extend the timer"
        )


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

                global note
                if len(players_joined["players"]) == 1:
                    note = await bot.send_message(players_joined["chat_id"],
                                                  "*Registration is in progress*\n\nRegistered:\n@" +
                                                  "\n@".join(map(str, (x.username for x in players_joined["players"]))))
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

            elif len(players_joined["players"]) >= 4:
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
