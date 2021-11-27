from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

"""INLINE KEYBOARD BUTTONS"""
inline_button_go = InlineKeyboardButton("Go", url='https://t.me/CeeebBot?start=a')
inline_keyboard_join = InlineKeyboardMarkup(row_width=2).add(inline_button_go)

inline_button_profile = InlineKeyboardButton('Profile🤵🏻', callback_data='Profile🤵🏻')
inline_button_help = InlineKeyboardButton('Help', callback_data='Help')
inline_button_back = InlineKeyboardButton('🔙', callback_data='🔙')
inline_button_addBot = InlineKeyboardButton("Add bot to server🕵🏻‍♂️", url='https://t.me/CeeebBot?startgroup=true')
inline_keyboard_start = InlineKeyboardMarkup(row_width=2).add(inline_button_addBot, inline_button_profile,
                                                              inline_button_help)
inline_keyboard_back = InlineKeyboardMarkup(row_width=2).add(inline_button_back)

button_join = KeyboardButton("Join game 🔗")
join_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(button_join)
