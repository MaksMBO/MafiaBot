from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btnAddBot = KeyboardButton("Add bot to server", url='https://t.me/CeeebBot?startgroup=true')
btnProfile = KeyboardButton('Profile🤵🏻')
btnHelp = KeyboardButton('Help')
btnBack = KeyboardButton('🔙Back')
mainMenu = ReplyKeyboardMarkup(resize_keyboard=True).add(btnAddBot, btnProfile, btnHelp)
menu2 = ReplyKeyboardMarkup(resize_keyboard=True).add(btnBack)
