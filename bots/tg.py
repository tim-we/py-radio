from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.parsemode import ParseMode
from radio.player import Player
from radio.library import ClipLibrary
from radio.audio.clips import MP3Clip, describe
import os
from typing import Any
from re import findall
from pathlib import Path
from pytube import YouTube


class Telegram:
    def __init__(self, token: str, player: Player, library: ClipLibrary):
        self._player = player
        self._library = library
        self._updater = Updater(token=token, use_context=True)
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
        youtube_handler = MessageHandler(Filters.regex(r'youtube\.com'), self._youtube)
        dispatcher.add_handler(youtube_handler)

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
            self._player.schedule(MP3Clip(file_path))
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Added `{}` to music library.".format(file_name),
                                     parse_mode=ParseMode.MARKDOWN)

    def _youtube(self, update: Any, context: Any) -> None:
        yt_id = findall(r'watch\?v=(\w+)', update.message.text)[0]
        url = r'https://www.youtube.com/watch?v={}'.format(yt_id)
        try:
            audio = YouTube(url).streams.filter(only_audio=True, subtype='mp4').first()
            file_path = audio.download(output_path=self._library.music.folder, filename=audio.default_filename)
            self._library.music.scan()
            self._player.schedule(MP3Clip(file_path))
        except KeyError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="I cannot access this video.")

    @staticmethod
    def _exit(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Terminating the radio!")
        if len(context.args) > 0:
            os._exit(int(context.args[0]))
        else:
            os._exit(0)

    def _history(self, update: Any, context: Any) -> None:
        history = '\n'.join(self._player.get_history(fmt="[{:02d}:{:02d}] `{}`"))
        if not history:
            context.bot.send_message(chat_id=update.effective_chat.id, text="The history is empty.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=history, parse_mode=ParseMode.MARKDOWN)

    def _skip(self, update: Any, context: Any) -> None:
        msg = "Skipping {}".format(describe(self._player.now()))
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        self._player.skip()

    @staticmethod
    def _unknown(update: Any, context: Any) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
