# -*- coding: utf-8 -*-
'''This module contains a class that creates new telegram bots. The final product of the module is a py file with a new bot.'''

import os
import sys
import sqlite3
import logging
from typing import List


class NotificationsFunctional:
    '''Contains methods for creating a bot that will send notifications'''

    @staticmethod
    def _notifications_functional(db_cursor, log, **kwargs) -> str:
        '''
        Adding the logic of sending notifications to certain users to the class being created.
        ----------------------
        users_type:[int] - 0 = list of notification recipients, 1 = the path to the file with the list of users, 2 = python code that returns a list of ids
        users:List[str] - data depending on the users_type parameter. If not specified, then by default an empty list/dictionary.
        accesses:List[str] (optional) - a list of possible accesses. If this parameter is specified, then it is worth specifying users in the form of a dictionary {"user_id": ["access 1", "access 3"]} (or specify accesses later).
                The access parameter can be used to send different messages depending on the user's position.
        notif_func:str (optional) - a code that will trigger notifications. Either the code of the function to be added to the bot, or the function of the imported module.
                You can leave None and send notifications via the <bot>.send method.
        notif_func_args: List[*args, **kwargs] (optional) - parameters of the function that triggers notifications.
                The first element of the list is a list of variables, the second element is a dictionary of variables and default values.
        '''

        init_code = ''
        code = ''

        try:
            users_type = kwargs.get('users_type')

            accesses = kwargs.get('accesses')
            if accesses is None:
                default_users = []
            else:
                default_users = {}
                init_code += ' '*8 + 'self.accesses = ' + str(accesses) + '\n'

            users = kwargs.get('users', default_users)

            if users_type == 0:
                init_code += ' '*8 + 'self.users = ' + str(users) + '\n'

            elif users_type == 1:
                path = users
                users = default_users
                with open(path, 'r', encoding='utf-8') as file:
                    all_users = file.readlines()

                for line in all_users:
                    user = line.strip()
                    if user:
                        if accesses is None:
                            users.append(user)
                        else:
                            data = user.split(',')
                            users[data[0]] = data[1:]

                init_code += ' '*8 + 'self.users = ' + str(users) + '\n'

            elif users_type == 2:
                response = db_cursor.execute('SELECT code FROM fragments WHERE id = "user_list_func"').fetchone()
                init_code += response[0].format(own_code=users)

            notif_func = kwargs.get('notif_func')
            if not notif_func is None:
                unformatted_code = ''
                response = db_cursor.execute('SELECT code FROM fragments WHERE id = "trigger"').fetchone()

                notif_args = kwargs.get('notif_func_args', [[], {}])
                notif_args_text = ', '.join(['self'] + notif_args[0])

                for key in notif_args[1]:
                    default = notif_args[1][key]
                    notif_args_text += f', {key} = {default}'

                notif_func = notif_func.replace('\t', '    ')
                for line in notif_func.split('\n'):
                    unformatted_code += ' '*8 + line + '\n'

                code = response[0].format(own_code=unformatted_code, notif_args=notif_args_text)

            return {'init': init_code, 'code': code}

        except AssertionError:
            log('AssertionError in MotherBot._notifications_functional\n', exc_info=True)
            print('Incorrect data is entered, the _notifications_functional method cannot be executed')
            input('Make sure the data is correct and try again')
            sys.exit(1)



class MotherBot:
    '''A class for creating telegram bots'''

    def __init__(self, loger):
        self.add_database()
        self.log = loger.error


    def add_database(self) -> None:
        '''Opening the database with code fragments for further use'''

        try:
            self.connect = sqlite3.connect('database/сode_fragments.sqlite')
            self.db_cursor = self.connect.cursor()

        except sqlite3.Error:
            input('Error:' + sqlite3.Error + '\n\nPress any button')
            sys.exit(code=1)


    def create_bot(self, file_name:str, types:List[int], **kwargs) -> None:
        '''
        Accepts a request to create a bot and executes it
        ----------------------
        file_name:str - unique file name
        types:List[int] - list of types that the bot should perform, where 0 - notifications, 1 - response to user messages, 2 - processing of chat/channel events
        modules:str (optional) - imported modules in text format. For example: import random, from typing import List, import threading as th...
        class_name:str (optional) - the name of the class to be created, if not specified, "file_name + _bot" is used
        class_doc:str (optional) - class description
        init_code:str (optional) - code of the initialization function, if it needs to be overloaded
        launch_сode:str (optional) - adds the startup code (if __name__ == '__main__': ...)
        init_args: List[*args, **kwargs] (optional) - parameters of the __init__ function.
                The first element of the list is a list of variables, the second element is a dictionary of variables and default values.
        '''

        class_name = kwargs.get('class_name')
        if class_name is None:
            class_name = file_name.capitalize() + '_bot'

        class_doc = kwargs.get('class_doc')
        if class_doc is None:
            class_doc = 'A class created using the library https://github.com/Kesha2447/easy-tg-bot'

        #Modules
        modules = kwargs.get('modules')
        if modules is None:
            modules = ''

        elif isinstance(modules, list):
            _modules_text = ''
            for module in modules:
                _modules_text += 'import ' + module + '\n'
            modules = _modules_text

        elif not isinstance(modules, str):
            modules = ''
            print('WARNING: Invalid data type, modules were not imported')

        #Init_code
        init_code = kwargs.get('init_code')
        if init_code is None:
            init_code = self.db_cursor.execute('SELECT code FROM fragments WHERE id = "def_init"').fetchone()[0]
        else:
            init_code = self._format_code(init_code, 4)

        init_code += '\n\n'

        #init args
        init_args = kwargs.get('init_args', [[], {}])
        init_args_text = ', '.join(['self'] + init_args[0])

        for key in init_args[1]:
            default = init_args[1][key]
            init_args_text += f', {key} = {default}'

        code = ''
        if 0 in types:
            additional_code = NotificationsFunctional._notifications_functional(self.db_cursor, self.log, **kwargs)
            init_code += additional_code['init']
            code += additional_code['code']

        if 1 in types:
            pass

        if 2 in types:
            pass

        response = self.db_cursor.execute('SELECT code FROM fragments WHERE id = "code_start"').fetchone()

        class_code = response[0].format(modules=modules, class_name=class_name, class_doc=class_doc, init_code=init_code, init_args=init_args_text)
        class_code += code

        launch_сode = kwargs.get('launch_сode')
        if not launch_сode is None:
            launch_сode = self._format_code(launch_сode, 4)

            response = self.db_cursor.execute('SELECT code FROM fragments WHERE id = "launch"').fetchone()
            class_code += response[0].format(own_code=launch_сode)

        with open('bots/' + file_name + '.py', 'w', encoding='utf-8') as file:
            file.write(class_code)


    def _format_code(self, code:str, spaces:int) -> str:
        '''Adds the specified number of spaces to each line of code'''

        unformatted_code = code.replace('\t', '    ')
        code = ''
        for line in unformatted_code.split('\n'):
            code += ' '*spaces + line + '\n'

        return code


def _new_loger(name, path):
    '''Enables logging'''

    dir_name = os.path.dirname(path)
    if dir_name and not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    #Trim the log file if it is too large
    if os.path.exists(path):
        with open(path, 'r') as file:
            content = file.read()

        if len(content) > 2000:
            with open(path, 'w') as file:
                file.write(content[1000:])

    loger = logging.getLogger(name)
    loger.setLevel(logging.INFO)

    fh = logging.FileHandler(path, encoding='utf-8')
    formatter = logging.Formatter("\n-->> %(name)s %(asctime)s %(levelname)s %(message)s", datefmt="%d.%m %H:%M:%S")
    fh.setFormatter(formatter)
    loger.addHandler(fh)

    return loger


def test_notif_bot(mother_bot):
    '''Creating a copy of the class from the module with examples, but with the help of our parent class'''

    init_code = "    '''\n    token:str - bot token received from https://t.me/BotFather\n    userslist[str] - users tokens received from https://t.me/getmyid_bot\n    '''\n\n    super().__init__(token)\n    self.users = users\n\n    self.last_changes = {}"
    notif_func = 'last_change = self.last_changes.get(filename)\n\nif not os.path.exists(filename):\n    if last_change is None:\n        msg = f\'🤔 File {filename} does not exist\'\n    else:\n        msg = f\'😱 Someone deleted or rename your file "{filename}"!\'\n        self.last_changes.pop(filename)\n\n    for user in self.users:\n        self.api.send_message(user, msg)\n\n    return 1\n\nif last_change is None:\n    self.last_changes[filename] = os.path.getmtime(filename)\n\n    text_time = time.ctime(self.last_changes[filename])\n    msg = f\'Starting to monitor the file "{filename}". Last updated {text_time}.\'\n\n    for user in self.users:\n        self.api.send_message(user, msg)\n\nelse:\n    change = os.path.getmtime(filename)\n\n    if last_change != change:\n        self.last_changes[filename] = change\n\n        text_time = time.ctime(self.last_changes[filename])\n        msg = f\'❗️Viu-viu! {text_time} someone touched your file {filename}!❗️\'\n\n        for user in self.users:\n            self.api.send_message(user, msg)\n\nreturn 0\n'
    launch_сode = "token = 'TOKEN'\nusers = ['571315321'] #usersID\ntelegram = NotificationsBot(token, users)\nwhile True:\n    status_code = telegram.notificationTrigger('data.txt')\n    if status_code:\n        print(f'The test is over with the status code {status_code}')\n        break\n    time.sleep(1)\n"

    mother_bot.create_bot('my_bot', [0], modules=['os', 'time'], class_name='NotificationsBot', class_doc='\n    A class showing how to create a bot that sends notifications to specified users.\n\n    We will receive a notification when someone changes our file. (Can be used to check the database for changes)\n    ',
                          init_code=init_code, init_args=[['token', 'users'], {}], notif_func=notif_func, notif_func_args=[['filename'], {}], launch_сode=launch_сode)


if __name__ == '__main__':
    loger = _new_loger('MotherBot', 'logs/error.log')
    try:
        mother_bot = MotherBot(loger)

        test_notif_bot(mother_bot)
        mother_bot.create_bot('empty', [1])
        print('End')
    except:
        loger.fatal('Unhandled exception:', exc_info=True)
        print('Unhandled exception. For more information, see logs/error.log')