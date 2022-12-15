# -*- coding: utf-8 -*-
'''Module with the parent class of telegram bot'''

import telebot
import threading as th
from typing import Callable, List


class TelegramBotParent:
    '''
    Class for create telegram bot
    ----------------------
    methods:
       add_listening - Add listening to messages from telegram
       add_keyboard_listening - Add listening pressing the button
       make_inline_keyboard - Creates a keyboard object to be used when sending a message to the user
       start_listen - Start listening to messages - it is START
    '''

    def __init__(self, token:str, parse_mode:str = None):
        '''
        Init new bot by parameters
        ----------------------
        token:str - bot token received from https://t.me/BotFather
        parse_mode: str/None - how to format text, HTML or MARKDOWN (None = usual text)
        '''

        self.api = telebot.TeleBot(token, parse_mode)


    def add_listening(self, handler:Callable, content_types:List[str] = None, commands:List[str] = None, func:Callable = None) -> None:
        '''
        Add listening to messages from telegram
        ----------------------
        handler: function - a function for processing a message like function(message). Other parameters are prohibited
        content_types: List[str] - type of messages. Default: ['text']. Available types: (text, audio, document, photo, sticker,
           video, video_note, voice, location, contact, new_chat_members, left_chat_member, new_chat_title, new_chat_photo, delete_chat_photo,
           group_chat_created, supergroup_chat_created, channel_chat_created, migrate_to_chat_id, migrate_from_chat_id, pinned_message, web_app_data)
        commands: List[str] - like ['start', 'help'], denotes commands like /start, /help
        func : function - the filter function should return True if the message fits. Like lambda msg: msg.document.mime_type == 'text/plain'
        '''

        if content_types is None:
            content_types = ['text']

        self.api.message_handler(content_types=content_types, commands=commands, func=func)(handler)


    def add_keyboard_listening(self, handler:Callable, func:Callable = None) -> None:
        '''
        Add listening pressing the button
        ----------------------
        handler: function - a function for processing a message like function(message). Other parameters are prohibited
        func: function - filter the responses to be processed. By default, all messages.
        '''

        if func is None:
            func = lambda call: True
        self.api.callback_query_handler(func=func)(handler)


    def make_inline_keyboard(self, buttons) -> telebot.types.InlineKeyboardMarkup:
        '''
        Creates a keyboard object to be used when sending a message to the user. Something like send_message(user_id, text, reply_markup=KEYBOARD)
        A keyboard handler is required to work
        ----------------------
        buttons: list/dict/iterable obj/str/int
            list = button name = value, button key = index
            dict = button name = dict key, button key = value
            iterable obj = button name and button key = index
            string and other = button name and button key = index
        '''

        keyboard = telebot.types.InlineKeyboardMarkup()

        if isinstance(buttons, list):
            i = 0
            for button in buttons:
                button_elem = telebot.types.InlineKeyboardButton(text=button, callback_data=str(i))
                keyboard.add(button_elem)
                i += 1

        elif isinstance(buttons, dict):
            for key in buttons:
                button_elem = telebot.types.InlineKeyboardButton(text=buttons[key], callback_data=str(key))
                keyboard.add(button_elem)

        elif not isinstance(buttons, str) and hasattr(buttons, '__iter__'):
            for button in buttons:
                button_elem = telebot.types.InlineKeyboardButton(text=button, callback_data=str(button))
                keyboard.add(button_elem)

        else:
            button_elem = telebot.types.InlineKeyboardButton(text=buttons, callback_data=str(buttons))
            keyboard.add(button_elem)

        return keyboard


    def start_listen(self, separate_thread:bool = True) -> None:
        '''
        Start listening to messages
        ----------------------
        separate_thread:bool - Whether to run in a separate thread or loop execution here
        '''

        tread_handler = th.Thread(target=self.api.infinity_polling)
        tread_handler.start()


    def send(self, msg, chat_id, keyboard=None):
        '''
        Sending a message to a user or to a chat
        ----------------------
        msg: str - a message to be sent
        chat_id: - the chat ID of the user or channel to send a message from the bot. You can pass a list.
                   IMPORTANT: you can only send a message to a user who has written to the bot at least 1 time
        keyboard: - The keyboard object that will be shown to the user
        '''

        try:
            if isinstance(chat_id, str) or isinstance(chat_id, int):
                chat_id = str(chat_id)
                self.api.send_message(chat_id, str(msg), reply_markup=keyboard)
            else:
                for user_id in chat_id:
                    self.api.send_message(user_id, str(msg), reply_markup=keyboard)
        except:
            print(f'''Failed to send message\nfile: {__file__}\nmsg: {msg}\nchat_id: {chat_id}\nkeyboard: {keyboard}''')



