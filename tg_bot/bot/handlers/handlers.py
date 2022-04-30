from telegram.ext import CallbackContext
from telegram import (
    Update, ChatAction,
    InlineKeyboardButton, InlineKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

from conf import logger

menu_btns = [
    [KeyboardButton('VPN серверы'), KeyboardButton('Выбрать тариф')],
    [KeyboardButton('Мои заказы'), KeyboardButton('Баланс')],
    [KeyboardButton('Пригласить друга')]
]

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    logger.info("START command entered")
    update.message.reply_text(
        'Привет!', 
        reply_markup=ReplyKeyboardMarkup(menu_btns)
    )

def echo(update: Update, context: CallbackContext) -> None:
    logger.info("Text message recived")
    update.message.reply_text(update.message.text, reply_markup=ReplyKeyboardRemove())