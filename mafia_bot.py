import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import markup

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['cats'])
async def cats(message: types.Message):
    with open('C:/Users/xomka/Downloads/Telegram Desktop/image_2021-02-27_20-03-11.png', 'rb') as photo:
        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # print(message.chat.type)
    await bot.send_message(message.from_user.id, f'Привет {message.chat.first_name}',
                           reply_markup=markup.mainMenu)


# async def update_data(users, user, server):
#     users[str(server.id)] = {}
#     if not str(user.id) in users[str(server.id)]:
#         users[str(server.id)][str(user.id)] = {}
#     elif not str(user.id) in users[str(server.id)]:
#         users[str(server.id)][str(user.id)] = {}


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
