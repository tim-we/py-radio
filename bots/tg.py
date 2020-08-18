from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from radio.player import Player
import logging
from time import sleep
from decouple import config
import os
from typing import Any


class Telegram:
    def __init__(self, player: Player):
        self._player = player
        self.updater = Updater(token=config('TG_TOKEN'), use_context=True)
        dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        exit_handler = CommandHandler('exit', self._exit)
        dispatcher.add_handler(exit_handler)
        skip_handler = CommandHandler('skip', self._skip)
        dispatcher.add_handler(skip_handler)
        unknown_handler = MessageHandler(Filters.command, self._unknown)
        dispatcher.add_handler(unknown_handler)

    def start(self) -> None:
        self.updater.start_polling()

    def stop(self) -> None:
        self.updater.stop()

    @staticmethod
    def _exit(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Terminating the radio!")
        if len(context.args) > 0:
            os._exit(int(context.args[0]))
        else:
            os._exit(0)

    def _skip(self, update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Skipped "+self._player.now())
        self._player.skip()

    @staticmethod
    def _unknown(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
