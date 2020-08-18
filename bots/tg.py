from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from time import sleep
from decouple import config


class Telegram:
    def __init__(self):
        self.updater = Updater(token=config('TG_TOKEN'), use_context=True)
        dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        start_handler = CommandHandler('start', self._start)
        dispatcher.add_handler(start_handler)
        echo_handler = MessageHandler(Filters.text & (~Filters.command), self._echo)
        dispatcher.add_handler(echo_handler)
        caps_handler = CommandHandler('caps', self._caps)
        dispatcher.add_handler(caps_handler)
        unknown_handler = MessageHandler(Filters.command, self._unknown)
        dispatcher.add_handler(unknown_handler)

    def start(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def _start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    def _echo(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

    def _caps(self, update, context):
        text_caps = ' '.join(context.args).upper()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

    def _unknown(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


tg = Telegram()
tg.start()

while True:
    sleep(10)
