"""Gif files for the game"""
gif_sunrise = open('Other/sunrise.gif', 'rb')
gif_kill = open('Other/Mafia_kill.gif', 'rb')
gif_do_not_kill = open('Other/mafia_dont_kill.gif', 'rb')
gif_sunset = open('Other/sunset.gif', 'rb')
gif_none_lynched = open('Other/no_one_lynched.gif', 'rb')
gif_lynching = open('Other/lynching.gif', 'rb')
gif_direct_lynching = open('Other/lynched_message.gif', 'rb')


"""Constants in the game"""
MIN_PLAYERS = 4


"""Management `mafia_bot.py` strings"""

ADMINISTRATOR_RIGHTS = """"Administrator rights have not been granted 
To start the game give me the following administrator rights: 
☑️ delete messages 
☑️ block users 
☑️ pin messages"""

REGISTRATION_START_STR = "Registration is open"
REGISTRATION_END_STR = "Registration is over"
REGISTRATION_NOT_STARTED_STR = "Registration is not started now"
REGISTRATION_IN_PROGRESS = "<b>Registration is in progress</b>\n\nRegistered:\n@"
REGISTRATION_DONE = "You have registered in the game, wait for the start✅"
ALREADY_REGISTERED_STR = "You are already registered, just wait⌛️"
NO_REGISTRATION_STR = "There is no game registered"
FIRST_NOTIFY_REGISTRATION_END = "Time until the end of registration 60 seconds"
SECOND_NOTIFY_REGISTRATION_END = "Time until the end of registration 60 seconds"
NOT_ENOUGH_STR = "Not enough players to start the game..."
MIN_PLAYERS_STR = "A minimum of four users must be registered to stop the timer"
GAME_START_STR = "<b>GAME IS STARTED</b>"
EXTEND_TIMER_STR = "Added +30 seconds to the duration of registration. Time left till the game begins: "
EXTEND_TIMER_CONDITION_STR = "You need to have at least two registered users to extend the timer"
ALLIES_STR = "Remember your allies: \n@"

"""`Game.py` strings"""

NIGHT_START = "<b>🌃 Night falls</b>\nOnly the most courageous and fearless take to the streets of the city. " \
              "Let's try to count their heads in the morning ..."
DAY_START = 'The sun rises, drying the blood spilled at night on the sidewalks ... morning ...'
LYNCHING = "<b>It's time to look for the guilty ones!</b>\nWho do you want to lynch?"
NO_ONE_KILLED = '<b>No one was killed that night</b>'
YOU_LYNCHED = "You were lynched"
YOU_KILLED = "<b>You were killed</b>"
DIVERSITY_STR = '<b>Voices diverged.</b>\nNo one was lynched.'
MAFIA_KILL_STR = "<b>It's time to kill!</b>\nChoose a victim "
POLICE_CHECK_STR = "<b>Choose who you want to check tonight.</b>\nChoose suspect:"
MEDIC_HEAL_STR = "<b>Who will you heal?</b>\nChoose a patient"
MAFIA_WON_STR = '<b>Mafia won</b>'
CIVILIANS_WON_STR = "<b>Civilians won</b>\n"



