import random
import math
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import markup
from aiogram.types import InlineKeyboardMarkup
from Roles import Mafia, Police, Medic, Civilian
from aiogram import Bot, Dispatcher
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
