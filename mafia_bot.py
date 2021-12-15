from Imports import *
from Game import Games
from Constants import *

MESSAGE_ID_NOTE = types.Message

is_registration = True
note = None
game = True
save_game = MemoryStorage()
players_joined = {}
game_number = {}



def admin_permissions_check(bot_permission):
    """ function to check if bot has enough permissions to moderate the chat while games"""
    return bot_permission['status'] == "administrator" and bot_permission["can_manage_chat"] \
           and bot_permission["can_delete_messages"] and bot_permission["can_restrict_members"] \
           and bot_permission["can_manage_voice_chats"] and bot_permission["can_pin_messages"]


async def check_admin(chat_id, bot_id):
    """ function to send rights which bot is needed to channel owners """
    bot_permission = await bot.get_chat_member(chat_id, bot_id)
    if admin_permissions_check(bot_permission):
        return True
    await bot.send_message(chat_id, ADMINISTRATOR_RIGHTS)
    return False


async def update_data(users, user):
    """ update user profile in this bot"""
    if str(user.id) not in users:
        users[str(user.id)] = {}
        users[str(user.id)]['Games played'] = 0
        users[str(user.id)]['Games won'] = 0


@dp.message_handler(commands=['game'])
async def registration(message: types.Message):
    """ function for registering players and perform game """
    global is_registration

    if message.chat.id < 0 and is_registration and await check_admin(message.chat.id, bot.id):
        global players_joined
        await message.reply(REGISTRATION_START_STR, reply_markup=markup.inline_keyboard_join)
        players_joined["chat_id"] = message.chat.id
        players_joined["players"] = []
        players_joined["time_remaining"] = 60
        is_registration = False

        await bot.send_message(message.chat.id, FIRST_NOTIFY_REGISTRATION_END)
        while players_joined["time_remaining"] > 0:
            players_joined["time_remaining"] -= 1
            if players_joined["time_remaining"] == 30:
                await bot.send_message(message.chat.id, SECOND_NOTIFY_REGISTRATION_END)
            if len(players_joined["players"]) >= 13:
                players_joined["time_remaining"] = 0
            await asyncio.sleep(1)
        await bot.send_message(message.chat.id, REGISTRATION_END_STR)
        if len(players_joined["players"]) < MIN_PLAYERS:
            await bot.send_message(message.chat.id, NOT_ENOUGH_STR)
            players_joined.clear()
            is_registration = True
        else:
            await bot.send_message(message.chat.id, GAME_START_STR, parse_mode="Markdown")
            with open('users.json', 'r') as f:
                users = json.load(f)
            for user in players_joined["players"]:
                await update_data(users, user)
                users[str(user.id)]["Games played"] += 1
            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)
            game_number[str(message.chat.id)] = Games(players_joined, message.chat.id)
            await game_number[str(message.chat.id)].give_roles()

            #informs the mafia about his allies (other mafias)
            for mafia in game_number[str(message.chat.id)].mafia_players:
                await bot.send_message(mafia.user_profile.id, ALLIES_STR +
                                       "\n@".join(map(str, (x.user_profile.username + "- 🤵🏼 Mafia" for x in
                                                            game_number[str(message.chat.id)].mafia_players)))
                )

            #start game
            while game_number[str(message.chat.id)].game:
                await game_number[str(message.chat.id)].night()

                await handlers_call()
                while len(game_number[str(message.chat.id)].kill_mafia) == 0 or \
                        game_number[str(message.chat.id)].doctor_heal == 0 or \
                        game_number[str(message.chat.id)].cherif_check == 0:
                    await asyncio.sleep(1)
                await game_number[str(message.chat.id)].mafia_kill()
                await game_number[str(message.chat.id)].cherif_night()
                await game_number[str(message.chat.id)].day()
                timer = 120
                while len(game_number[str(message.chat.id)].lynch) < \
                        len(game_number[str(message.chat.id)].civilian_players) + \
                        len(game_number[str(message.chat.id)].mafia_players) and timer >= 0:
                    if timer == 60:
                        ############################################################################################
                        await bot.send_message(players_joined["chat_id"], "One minute remaining")
                    if timer == 30:
                        #######################################################################################
                        await bot.send_message(players_joined["chat_id"], "30 seconds remaining")
                    await asyncio.sleep(1)
                    timer -= 1
                await game_number[str(message.chat.id)].lynched()
            is_registration = True


async def handlers_call():
    """function to call handlers in game"""
    @dp.message_handler()
    async def chat_moderating(mes: types.Message):
        """ handles and deletes messages of users who are not playing or of players who write during the night """
        if (str(mes.from_user.id) not in map(str, (x.user_profile.id for x in
                                                   game_number[str(mes.chat.id)].civilian_players +
                                                   game_number[str(mes.chat.id)].mafia_players)) or
            game_number[str(mes.chat.id)].end_night) \
                and game_number[str(mes.chat.id)].game:
            await mes.delete()

    @dp.callback_query_handler(markup.cb.filter(button_for="Mafia"))
    async def callbacks_mafia(call: types.CallbackQuery, callback_data: dict):
        """ Function to handle the choice of the mafia who to kill """
        game_number[callback_data['id_game']].kill_mafia.append(callback_data['user_id'])
        await editing_message(game_number[callback_data['id_game']], callback_data,
                              game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*Mafia loaded weapons*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Doctor"))
    async def callbacks_doctor(call: types.CallbackQuery, callback_data: dict):
        """ Function to handle the choice of the doctor who to heal """
        game_number[callback_data['id_game']].doctor_heal = callback_data['user_id']
        await editing_message(game_number[callback_data['id_game']], callback_data,
                              game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*The doctor went out on night duty*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Cherif"))
    async def callbacks_cherif(call: types.CallbackQuery, callback_data: dict):
        """ Function to handle the choice of the mafia who to check """
        game_number[callback_data['id_game']].cherif_check = callback_data['user_id']
        await editing_message(game_number[callback_data['id_game']], callback_data,
                              game_number[callback_data['id_game']].role_dict[call.from_user.id])
        await bot.send_message(
            players_joined['chat_id'], '*The Commissioner went to look for the guilty*', parse_mode="Markdown"
        )

    @dp.callback_query_handler(markup.cb.filter(button_for="Day"))
    async def callbacks_day(call: types.CallbackQuery, callback_data: dict):
        """ Function to handle the choice of the player on the day who to lynch """
        game_number[callback_data['id_game']].lynch.append(callback_data['user_id'])
        await editing_message(game_number[callback_data['id_game']], callback_data,
                              game_number[callback_data['id_game']].players_dict[call.from_user.id])


async def editing_message(games, callback_data, dicts):
    """ function for editing a message, after pressing a button, so that the player cannot press them anymore  """
    for civilian in games.civilian_players:
        if str(callback_data['user_id']) == str(civilian.user_profile.id):
            await dicts.edit_text(f"You have chosen a {civilian.user_profile.username}")
    for mafia in games.mafia_players:
        if str(callback_data['user_id']) == str(mafia.user_profile.id):
            await dicts.edit_text(f"You have chosen a {mafia.user_profile.username}")


@dp.callback_query_handler(text="+30s")
async def timer_extend(call: types.CallbackQuery):
    """ function to add 30 seconds to timer during the registration"""
    if len(players_joined["players"]) > 1:
        players_joined["time_remaining"] += 30
        await bot.send_message(call.message.chat.id, EXTEND_TIMER_STR + f"{players_joined['time_remaining']}.")
    else:
        await bot.send_message(call.message.chat.id, EXTEND_TIMER_CONDITION_STR)


@dp.message_handler(commands=['start'])
async def send_welcome_message(message: types.Message):
    """ functions of start command(they are different in direct messages, chat and after pressing GO in registration """
    if message.chat.id > 0:
        if message.get_args() == 'a':

            if players_joined["time_remaining"] == 0:
                await bot.send_message(message.from_user.id, NO_REGISTRATION_STR)
            elif message.from_user in players_joined["players"]:
                await bot.send_message(message.from_user.id, ALREADY_REGISTERED_STR)
            else:
                await bot.send_message(message.from_user.id, REGISTRATION_DONE)
                players_joined["players"].append(message.from_user)
########################################################################################################################
                global note
                if len(players_joined["players"]) == 1:
                    note = await bot.send_message(
                        players_joined["chat_id"], REGISTRATION_IN_PROGRESS +
                                                   '\n@'.join(map(str, (x.username for x in players_joined["players"])))
                    )
                else:
                    await note.edit_text(
                        REGISTRATION_IN_PROGRESS + '\n@'.join(map(str, (x.username for x in players_joined["players"])))
                    )
        else:
            await bot.send_message(message.from_user.id,
                                   "Hi! {0.first_name}, 🕴 I'm mafia bot ".format(message.from_user),
                                   reply_markup=markup.inline_keyboard_start)

        await message.delete()
    else:
        if await check_admin(message.chat.id, bot.id):
            if len(players_joined) == 0:
                error = await bot.send_message(message.chat.id, REGISTRATION_NOT_STARTED_STR)
                await asyncio.sleep(5)
                await error.delete()

            elif len(players_joined["players"]) >= 4:
                players_joined["time_remaining"] = 0
            else:
                error = await bot.send_message(message.chat.id, MIN_PLAYERS_STR)
                await asyncio.sleep(10)
                await error.delete()
            await message.delete()


@dp.callback_query_handler(text="Profile🤵🏻")
async def creating_buttons(call: types.CallbackQuery):
    """ function that sends user profile """
    await call.message.delete()
    with open('users.json', 'r') as f:
        users = json.load(f)
    await bot.send_message(call.from_user.id, f"👤*{call.from_user.first_name if call.from_user.first_name else ''} "
                                              f"{call.from_user.last_name if call.from_user.last_name else ''}*"
                                              f"\n\nGames played: {users[str(call.from_user.id)]['Games played'] }"
                                              f"\nGames won: {users[str(call.from_user.id)]['Games won'] }",
                           reply_markup=markup.inline_keyboard_back, parse_mode="Markdown")


@dp.callback_query_handler(text="Help")
async def creating_buttons(call: types.CallbackQuery):
    """ sends help in chat """
    await bot.send_message(call.from_user.id, "It`s help!\nTo start game write /game\nTo start game before "
                                              "timer's up write /start in chat")


@dp.callback_query_handler(text="🔙")
async def creating_buttons(call: types.CallbackQuery):
    """ back to main menu """
    await call.message.delete()
    await bot.send_message(call.from_user.id,
                           "Hi! {0.first_name}, 🕴 I'm mafia bot ".format(call.from_user),
                           reply_markup=markup.inline_keyboard_start)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
