# -*- coding: utf-8 -*-
'''The basic module for testing the functionality of the bots_creator module'''

import os
import sys
import sqlite3
import unittest

sys.path.append("..")
import bots_creator


class BaseTest(unittest.TestCase):
    '''Base class for testing'''

    test_files = [] #List of files to delete after execution


    def setUp(self):
        loger = bots_creator._new_loger('MotherBotTest', 'error.log')
        self.mother_bot = bots_creator.MotherBot(loger)
        self._add_database('results')


    def tearDown(self):
        '''Deleting the files that were used during testing'''

        for path in self.test_files:
            if os.path.isfile(path):
                os.remove(path)


    def _add_database(self, name):
        '''Opening the database with code fragments with expected results'''

        try:
            path = os.path.dirname(__file__)
            self.connect = sqlite3.connect(path + f'/{name}.sqlite3')
            self.db_cursor = self.connect.cursor()

        except sqlite3.Error as err:
            input('Error: ' + str(err) + '\n\nPress any button')
            sys.exit(code=1)


    def _get_code(self, code_id):
        '''Get the code from the database'''

        response = self.db_cursor.execute(f'SELECT code FROM fragments WHERE id = "{code_id}"').fetchone()
        return response[0]


class General(BaseTest):
    '''A class for testing functions common to all types of bots'''

    test_files = ['bots/bot_1.py', 'bots/bot_2.py', 'bots/bot_3.py', 'bots/test1.py', 'bots/test2.py', 'bots/test3.py']


    def test_file_creating_1(self):
        '''We check that the file is being created successfully'''

        self.mother_bot.create_bot('bot_1', [], class_name='TestBot')

        with open(self.test_files[0]) as f:
            code = f.read()

        self.assertEqual(code, self._get_code('empty'))


    def test_file_creating_2(self):
        '''We check that the file is being created successfully'''

        self.mother_bot.create_bot('bot_2', [], modules=['os', 'time'])

        with open(self.test_files[1]) as f:
            code = f.read()

        self.assertEqual(code[116:116 + 40], 'import os\nimport time\n\nimport basic_bot\n')


    def test_file_creating_3(self):
        '''We check that the file is being created successfully'''

        self.mother_bot.create_bot('bot_3', [], modules='import os\nimport time')

        with open(self.test_files[2]) as f:
            code = f.read()

        self.assertEqual(code[116:116 + 40], 'import os\nimport time\n\nimport basic_bot\n')


    def test_class_name_1(self):
        '''The test of the correct formation of the class name'''

        self.mother_bot.create_bot('test1', [])

        with open(self.test_files[3]) as f:
            code = f.read()

        start_pos = code.find('class')
        end_pos = code.find('(basic_bot')

        class_name = code[start_pos + 6: end_pos]

        self.assertEqual(class_name, 'Test1_bot')


    def test_class_name_2(self):
        '''The test of the correct formation of the class name'''

        self.mother_bot.create_bot('test2', [], class_name='UniqueName')

        with open(self.test_files[4]) as f:
            code = f.read()

        start_pos = code.find('class')
        end_pos = code.find('(basic_bot')

        class_name = code[start_pos + 6: end_pos]

        self.assertEqual(class_name, 'UniqueName')


    def test_format_code(self):
        '''Testing the correct formatting of the code'''

        code = '1\n2\n3\n\n456\tsdsfg\nfsa\nif True:\n    a = b'
        result = self.mother_bot._format_code(code, 4)

        self.assertEqual(result, '    1\n    2\n    3\n\n    456\tsdsfg\n    fsa\n    if True:\n        a = b\n')


    def test_launch(self):
        '''Сheck how a launch code will be added'''

        launch = "bot = Test3()\nbot.send('Hello Test')"
        self.mother_bot.create_bot('test3', [], class_name='TestBot', launch_сode=launch)

        with open(self.test_files[5]) as f:
            code = f.read()

        self.assertEqual(code, self._get_code('empty') + self._get_code('launch'))


class Notifications(BaseTest):
    '''A class for testing the creation of bots that send notifications'''

    test_files = ['users.txt', 'users1.txt']

    def test_user_type_0(self):
        '''List of notification recipients'''

        code = self.mother_bot.notifications.functional(users_type=0, users=['000000', '111111'])
        self.assertEqual(code['init'], "        self.users = ['000000', '111111']\n")


    def test_user_type_1(self):
        '''The path to the file with the list of users'''

        with open(self.test_files[0], 'w') as f:
            f.write('000000\n111111')

        code = self.mother_bot.notifications.functional(users_type=1, users=self.test_files[0])
        self.assertEqual(code['init'], "        self.users = ['000000', '111111']\n")


    def test_user_type_2(self):
        '''Python code that returns a list of ids'''

        code = self.mother_bot.notifications.functional(users_type=2, users="self.usets = ['000000', '111111']")
        self.assertEqual(code['init'], self._get_code('user_type_2'))


    def test_accesses_0(self):
        '''List of users and their accesses'''

        code = self.mother_bot.notifications.functional(users_type=0, users={'000000': ['user', 'admin'], '111111': ['user']}, accesses=['user', 'admin'])
        self.assertEqual(code['init'], self._get_code('access'))


    def test_accesses_1(self):
        '''List of users and their accesses'''

        with open(self.test_files[1], 'w') as f:
            f.write('000000,user,admin\n111111,user')

        code = self.mother_bot.notifications.functional(users_type=1, users=self.test_files[1], accesses=['user', 'admin'])
        self.assertEqual(code['init'], self._get_code('access'))


    def test_add_notif_func(self):
        '''Testing the addition of a separate function for notifications'''

        code = self.mother_bot.notifications.functional(notif_func=self._get_code('notif_function'), notif_func_args=[['name', 'file', '*args', '**kwargs'], {'is_def': False}])
        self.assertEqual(code['code'], self._get_code('notif_func_res'))


if __name__ == '__main__':
    unittest.main()