# -*- coding: utf-8 -*-
'''Example of a bot telegram based on a template'''

import os
import sys
import time
import random
import basic_bot
from typing import List


class NotificationsBot(basic_bot.TelegramBotParent):
    '''
    A class showing how to create a bot that sends notifications to specified users.

    We will receive a notification when someone changes our file. (Can be used to check the database for changes)
    '''

    def __init__(self, token:str, users:List[str]):
        '''
        token:str - bot token received from https://t.me/BotFather
        userslist[str] - users tokens received from https://t.me/getmyid_bot
        '''

        super().__init__(token)
        self.users = users

        self.last_changes = {}


    def start(self, filename:str) -> int:
        '''
        We check the file changes and if they have occurred, we send a notification in telegram
        ----------------------
        filename - we are following the change of this file
        '''

        last_change = self.last_changes.get(filename)

        if not os.path.exists(filename):
            if last_change is None:
                msg = f'🤔 File {filename} does not exist'
            else:
                msg = f'😱 Someone deleted or rename your file "{filename}"!'
                self.last_changes.pop(filename)

            for user in self.users:
                self.api.send_message(user, msg)

            return 1

        if last_change is None:
            self.last_changes[filename] = os.path.getmtime(filename)

            text_time = time.ctime(self.last_changes[filename])
            msg = f'Starting to monitor the file "{filename}". Last updated {text_time}.'

            for user in self.users:
                self.api.send_message(user, msg)

        else:
            change = os.path.getmtime(filename)

            if last_change != change:
                self.last_changes[filename] = change

                text_time = time.ctime(self.last_changes[filename])
                msg = f'❗️Viu-viu! {text_time} someone touched your file {filename}!❗️'

                for user in self.users:
                    self.api.send_message(user, msg)

        return 0



class ListenerBot(basic_bot.TelegramBotParent):
    '''The class shows an example of a bot that responds to bot messages'''

    def __init__(self, token):
        '''
        When initializing, we add listening for messages
        ----------------------
        token:str - bot token received from https://t.me/BotFather
        '''

        super().__init__(token, 'Markdown')
        self.add_listening(self._create_answers)

        self.dialog = {}
        self.default_answer = 'This command is not available'

        self._last_id = 0


    def start(self) -> None:
        '''Starting to listen for events'''

        self.start_listen()


    def add_answers(self, phrases:List[str], answer:str, answer_id:str = None, consider_case:bool = False) -> None:
        '''
        Adds new commands to the bot right while the script is running
        ----------------------
        answer:List[List, str] - The object containing the answers consists of a list of the user's words and a line with the answer
        answer_id:str - response id. An optional parameter, but to be able to edit or delete responses, it is worth specifying
        consider_case: bool - Do need to be case-sensitive
        '''

        if answer_id is None:
            answer_id = 'self-id=' + str(self._last_id)
            self._last_id += 1

        if not consider_case:
            phrases_case = phrases
            phrases = []

            for phrase in phrases_case:
                phrases.append(phrase.lower())

        remark = {
            'phrases': phrases,
            'answer': answer,
            'edit_case': not consider_case
        }

        self.dialog[answer_id] = remark


    def _create_answers(self, message) -> None:
        '''We respond to the user's message if it is in the dialog list, otherwise we respond with a standard message'''

        msg = message.text.strip()

        for answer_id in self.dialog:
            remark = self.dialog[answer_id]

            if remark['edit_case']:
                msg = msg.lower()


            if msg in remark['phrases']:
                answer = remark['answer']
                break
        else:
            answer = self.default_answer

        self.api.send_message(message.from_user.id, answer)



class BotWithKeyboard(ListenerBot):
    ''''''

    def __init__(self, token):
        '''
        When initializing, we add listening for keyboard
        ----------------------
        token:str - bot token received from https://t.me/BotFather
        '''

        super().__init__(token)

        self.keyboard_actions = {}

        self.add_keyboard_listening(self._process_keyboard)
        self.default_keyboard = None


    def add_keyboard_actions(self, actions:dict) -> None:
        '''
        Adds new keyboard click handlers
        ----------------------
        actions: dict[str: list] - A dictionary describing what to do when the button is pressed. The dictionary key must match the key of the button on the keyboard to be processed.
            The dictionary value consists of 2 elements. The first - value - can be str or function without parameters (if this function returns text, then it will also be used in the response).
            The second value is the new keyboard that needs to be displayed, if not, pass None
            Example:{'yes': ['Cool', None], 'no': [lambda: 'May be ' + random.choice(names) + '?', keyboard]}
        '''

        for key in actions:
            self.keyboard_actions[key] = actions[key]


    def _create_answers(self, message) -> None:
        '''We respond to the user's message if it is in the dialog list, otherwise we respond with a standard message'''

        msg = message.text.strip()

        for answer_id in self.dialog:
            remark = self.dialog[answer_id]

            if remark['edit_case']:
                msg = msg.lower()


            if msg in remark['phrases']:
                answer = remark['answer']
                break
        else:
            answer = self.default_answer

        self.api.send_message(message.from_user.id, answer, reply_markup=self.default_keyboard)


    def _process_keyboard(self, click) -> None:
        '''We give the answer depending on the button pressed'''

        user_id = click.from_user.id
        button_id = click.data

        for key in self.keyboard_actions:
            if button_id == key:
                action = self.keyboard_actions[key]
                if callable(action[0]):
                    result = action[0]()
                    if isinstance(result, str):
                        self.api.send_message(user_id, result, reply_markup=action[1])
                        self.api.edit_message_reply_markup(chat_id=user_id, message_id=click.message.id, reply_markup=None)
                    else:
                        self.api.edit_message_reply_markup(chat_id=user_id, message_id=click.message.id, reply_markup=action[1])

                else:
                    self.api.send_message(user_id, action[0], reply_markup=action[1])
                    self.api.edit_message_reply_markup(chat_id=user_id, message_id=click.message.id, reply_markup=None)


def test1(token:str) -> None:
    '''Sending notifications to specific users'''




def test2(token:str) -> None:
    '''Responses to user messages'''

    telegram = ListenerBot(token)

    answers = [
        [['hello', 'hi', 'yo', '/start'], 'Hi, I\'m a bot. List of commands by command /help.'],
        [['/help'], 'List of commands: \n/start\n/name\n/autor\n/help'],
        [['name', '/name'], 'I don\'t have name...'],
        [['author', 'creator', 'maker', '/autor'], 'Right here: https://github.com/Kesha2447/']
    ]

    telegram.default_answer = 'List of commands: \n/start\n/name\n/autor\n/help'

    for answer in answers:
        telegram.add_answers(*answer)

    telegram.start()


def test3(token:str) -> None:
    '''A mini-game with walking buttons'''

    telegram = BotWithKeyboard(token)

    answers = [
        [['hello', 'hi', 'yo', '/start'], f'Hi, is your name Mark?'],
    ]

    keyboard = telegram.make_inline_keyboard({'yes': 'Yes', 'no': 'No'})
    telegram.default_keyboard = keyboard

    names = ['Ben', 'Muhamed', '我不懂中文', 'Afanasiy', 'Lize', '0100101010101', 'Kate', 'Sintax Error', 'Name', 'London', 'Max', 'పేరు లేని']
    keyboard_actions = {
        'yes': ['Cool😎', None],
        'no': [lambda: 'May be ' + random.choice(names) + '?', keyboard]
     }

    for answer in answers:
        telegram.add_answers(*answer)

    telegram.add_keyboard_actions(keyboard_actions)
    telegram.start()


if __name__ == '__main__':
    token = '1079547037:AAEgDk4U5CPiOnKr-ov7Wy6soduTzkD1UQE'
    test_num = input('Enter the test number (1-3) = ')

    if test_num.strip() == '1':
        test1(token)
    elif test_num.strip() == '2':
        test2(token)
    elif test_num.strip() == '3':
        test3(token)
    else:
        print('From 1 to 3!')
