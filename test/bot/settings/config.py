#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import configparser
import io

import bot.settings.settings as settings


def create_config():

    config = configparser.ConfigParser()
    config.add_section('Settings')
    config.set('Settings', 'BOT_TOKEN', '1156110547:AAEZ4_V8ALdpyaMeYeQhzzi1UXMbLjoJ5gg')
    config.set('Settings', 'CHANNEL_ID', '0')
    config.set('Settings', 'ADMIN_ID', '0')
    config.set('Settings', 'QIWI_NUMBER', '+777777777777')
    config.set('Settings', 'QIWI_TOKEN', 'token')
    config.set('Settings', 'chat', 'url')
    config.set('Settings', 'support', 'url')
    config.set('Settings', 'results', 'url')
    config.set('Settings', 'percent_admin', '20')

    with open(settings.path, 'w') as config_file:
        config.write(config_file)


def check_config_file():

    if not os.path.exists(settings.path):
        create_config()

        print('\nSettings.cfg created, configure it, to go send the "go" command')
        
        while True:
            if input('...') == 'go':
                break
    else:
        pass
    

def read_config(setting):
    config = configparser.ConfigParser()
    config.read(settings.path)

    setting = config.get('Settings', setting)
    
    return setting
