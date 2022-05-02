from telegram.ext import CallbackContext
from telegram import (
    Update, ChatAction,
    InlineKeyboardButton, InlineKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from settings import logger
from utils.texts import get_text
from utils.states import State
from .utils.handlers import send_message
from models import *


menu_btns = [
    [KeyboardButton('VPN серверы'), KeyboardButton('Выбрать тариф')],
    [KeyboardButton('Мои заказы'), KeyboardButton('Баланс')],
    [KeyboardButton('Пригласить друга')]
]

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("START command entered")
    set_state(user.id, State.HELLO.value)
    send_message(user.id, text=get_text('start_text'), reply_markup=ReplyKeyboardMarkup(menu_btns))

def echo(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    state = get_state(user.id)
    text = update.message.text
    logger.info(f"Text message recived, state: {state}")
    send_message(user.id, text=update.message.text, reply_markup=ReplyKeyboardRemove())
