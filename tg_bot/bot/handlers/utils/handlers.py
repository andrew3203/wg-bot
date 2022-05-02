from telegram import ParseMode, Bot
from telegram.error import Unauthorized
from typing import Optional, Dict, List

from settings import TELEGRAM_TOKEN

from views import *


def send_message(user_id, text, parse_mode=ParseMode.HTML, reply_markup=None) -> None:

    bot = Bot(TELEGRAM_TOKEN)

    try:
        message = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
    except Unauthorized:
        User.update_user(user_id, is_active=False)
    else:
        User.update_user(user_id, is_active=True)
