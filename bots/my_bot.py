# -*- coding: utf-8 -*-
'''The file was created automatically. Source: https://github.com/Kesha2447/easy-tg-bot'''

import os
import time

import basic_bot


class NotificationsBot(basic_bot.TelegramBotParent):
    '''
    A class showing how to create a bot that sends notifications to specified users.

    We will receive a notification when someone changes our file. (Can be used to check the database for changes)
    '''

    def __init__(self, token, token, users):
        '''
        token:str - bot token received from https://t.me/BotFather
        userslist[str] - users tokens received from https://t.me/getmyid_bot
        '''

        super().__init__(token)
        self.users = users

        self.last_changes = {}


    def notificationTrigger(self, filename):
        '''Event that triggers notifications'''
        
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
        

if __name__ == '__main__':
    token = 'TOKEN'
    users = ['571315321'] #usersID
    telegram = NotificationsBot(token, users)
    while True:
        status_code = telegram.notificationTrigger('data.txt')
        if status_code:
            print(f'The test is over with the status code {status_code}')
            break
        time.sleep(1)

