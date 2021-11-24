import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.delete()
    await message.reply(" ")
    await bot.send_message(message.from_user.id,
                           "Hi! {0.first_name}, I'm mafia bot!".format(
                               message.from_user), reply_markup=markup.mainMenu)


@dp.message_handler()
async def creating_buttons(message: types.Message):
    if message.text == 'Profile🤵🏻':
        await message.delete()
        await bot.send_message(message.from_user.id, "👤*{0.first_name}*\n\nGames played: \nGames won: ".format(
            message.from_user), reply_markup=markup.menu2, parse_mode="Markdown")
    if message.text == '🔙Back':
        await message.delete()
        await bot.send_message(message.from_user.id, "M", reply_markup=markup.mainMenu)



# async def update_data(users, user, server):
#     users[str(server.id)] = {}
#     if not str(user.id) in users[str(server.id)]:
#         users[str(server.id)][str(user.id)] = {}
#     elif not str(user.id) in users[str(server.id)]:
#         users[str(server.id)][str(user.id)] = {}


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
