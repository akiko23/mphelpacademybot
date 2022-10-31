import aiogram.dispatcher.middlewares
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from db import Database
from pyqiwip2p import QiwiP2P
import os
import logging
from flask import Flask, request

BOT_TOKEN = '5426371103:AAHxzZ4or1O9sIRPpegcx_mCB76R1a0t6OM'

bot = Bot(BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database()

server = Flask(__name__)
logger = aiogram.dispatcher.middlewares.log
logger.setLevel(logging.DEBUG)

GROUP_ID = '-1001621949125'
APP_URL = 'https://academyhelperbot.herokuapp.com/' + BOT_TOKEN

UKASSA_TOKEN = "381764678:TEST:44230"
SBER_TOKEN = '401643678:TEST:df285492-0a8c-4c66-9b63-2fa28cb6ec59'

p2p = QiwiP2P(auth_key='eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6InNzczVvMC0wMCIsInVzZXJfaWQiOiI3OTg5NzUwNTg2MCIsInNlY3JldCI6ImI2MmE1MWYzYmViOTliZmJjYTAwM2U1YjFiNmM4MmQ1MTQ0Mzg5MGJhZWVlMjAxMmZlZTdhYmExZDFiM2IyMjUifX0=')
