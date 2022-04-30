
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from handlers.handlers import *
from conf import TELEGRAM_TOKEN


def setup_dispatcher(dispatcher) -> None:

    dispatcher.add_handler(CommandHandler("start", start))

    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, echo)
    )

    return dispatcher


def start_polling():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher = setup_dispatcher(dispatcher)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_polling()
