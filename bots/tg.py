from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.parsemode import ParseMode
from radio.player import Player
from radio.library import ClipLibrary
from decouple import config
import os
from typing import Any
from re import findall
from pathlib import Path


class Telegram:
    def __init__(self, player: Player, library: ClipLibrary):
        self._player = player
        self._library = library
        self._updater = Updater(token=config('TG_TOKEN'), use_context=True)
        dispatcher = self._updater.dispatcher
        exit_handler = CommandHandler('exit', self._exit)
        dispatcher.add_handler(exit_handler)
        skip_handler = CommandHandler('skip', self._skip)
        dispatcher.add_handler(skip_handler)
        history_handler = CommandHandler('history', self._history)
        dispatcher.add_handler(history_handler)
        unknown_handler = MessageHandler(Filters.command, self._unknown)
        dispatcher.add_handler(unknown_handler)
        mp3_handler = MessageHandler(Filters.audio, self._download_media)
        dispatcher.add_handler(mp3_handler)

    def start(self) -> None:
        self._updater.start_polling()

    def stop(self) -> None:
        self._updater.stop()

    def _download_media(self, update: Any, context: Any) -> None:
        audio = update.message.audio
        file = context.bot.get_file(audio.file_id)
        title = audio.title
        performer = audio.performer
        extension = findall(r'.*(\.\w{1,4})', file.file_path)[0]
        if not performer:
            file_name = title
        else:
            file_name = performer+' - '+title
        file_path = self._library.music.folder+'/'+file_name+extension
        if Path(file_path).is_file():
            context.bot.send_message(chat_id=update.effective_chat.id, text="This song already exists.")
        else:
            file.download(file_path)
            self._library.music.scan()
            context.bot.send_message(chat_id=update.effective_chat.id, text="Added `"+file_name+"` to music library.",
                                     parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    def _exit(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Terminating the radio!")
        if len(context.args) > 0:
            os._exit(int(context.args[0]))
        else:
            os._exit(0)

    def _history(self, update: Any, context: Any) -> None:
        history_list = ['`'+s+'`' for s in self._player.get_history()]
        history = '\n'.join(history_list)
        if not history:
            context.bot.send_message(chat_id=update.effective_chat.id, text="The history is empty.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=history, parse_mode=ParseMode.MARKDOWN)

    def _skip(self, update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Skipped "+self._player.now())
        self._player.skip()

    @staticmethod
    def _unknown(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
