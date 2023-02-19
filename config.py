import aiogram.dispatcher.middlewares
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import Database
from pyqiwip2p import QiwiP2P
import os, logging
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database()

server = Flask(__name__)
logger = aiogram.dispatcher.middlewares.log
logger.setLevel(logging.DEBUG)

GROUP_ID = os.environ.get("GROUP_ID")
APP_URL = 'https://academyhelperbot.herokuapp.com/' + BOT_TOKEN

UKASSA_TOKEN = os.environ.get("UKASSA_TOKEN")
SBER_TOKEN = os.environ.get("SBER_TOKEN")

p2p = QiwiP2P(auth_key=os.environ.get("QIWI_AUTH_KEY"))
