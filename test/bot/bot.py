#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import datetime
import random
import sqlite3
import threading
import time

from bot.functions.logger import *

import bot.settings.config as config
import bot.menu.bot_menu as menu
import bot.menu.names_btns_menu as names_btns
import bot.functions.functions as func
import bot.settings.texts as texts

import traceback

def start():
    config.check_config_file()

    logging.info(f'BOT START')
    bot = telebot.TeleBot(config.read_config('bot_token'), threaded=False)

    @bot.message_handler(commands=['start'])
    def handler_start(message):
        chat_id = message.chat.id

        func.first_join(chat_id, message.from_user.first_name, message.from_user.username)

        bot.send_message(
            chat_id=chat_id,
            text='🍒Привет, держи менюшку',
            reply_markup=menu.main_menu()
        )
    
    
    @bot.message_handler(commands=['admin'])
    def admin(message):
        chat_id = message.chat.id
        if func.check_admin(chat_id) == True:
            bot.send_message(
                chat_id=chat_id,
                text='🍒Привет, держи менюшку админа',
                reply_markup=menu.admin_menu()
            )


    @bot.message_handler(content_types=['text'])
    def send_message(message):
        chat_id = message.chat.id
        message_id = message.message_id
        
        if message.text == names_btns.main_menu[0]: # 🎲 Рулетка
            response = func.get_info_active_game()
            bot.send_message(
                chat_id=chat_id,
                text=texts.game_1.format(
                    response[2],
                    response[1],
                    func.check_bets_for_info(),
                    response[0]
                ),
                reply_markup=menu.game_menu()
            )
        
        if message.text == names_btns.main_menu[1]: # 👤 Мой профиль
            bot.send_message(
                chat_id=chat_id,
                text=f'🧟‍♂ id: {chat_id}\n'
                     f'💰 Баланс: {func.check_user_balance(chat_id)}',
                reply_markup=menu.profile_menu()
            )

        if message.text == names_btns.main_menu[2]: # 🚀 О проекте
            info = func.check_game_info()

            bot.send_message(
                chat_id=chat_id,
                text=f'🎰 Название проекта - Это игровой бот с выводом денег.\n'
                     f'За все время, игроками было сыграно {info[1]} игр на сумму {info[0]} RUB',
                reply_markup=menu.info_menu()
            )


    @bot.callback_query_handler(func=lambda call: True)
    def handler_call(call):
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        if call.data == 'deposit':
            response = func.deposit_qiwi(chat_id)

            date = str(datetime.datetime.now())[:19]
            
            info = func.Check_payment(chat_id)
            func.check_payment_dict[chat_id] = info
            info = func.check_payment_dict[chat_id]
            info.code = response[0]
            info.date = date
            info.markup = response[1]

            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=texts.check_payment.format(
                        config.read_config("qiwi_number"),
                        response[0],
                        date
                        ),
                reply_markup=response[1],
                parse_mode='html'
            )
        
        if call.data == 'check_payment':
            info = func.check_payment_dict[chat_id]

            if func.check_payment(chat_id) == True:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text='✅ Баланс успешно зачислен!'
                )
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text='❌ Платеж не найден'
                )
        
        if call.data == 'winthdraw':
            check = func.check_user_balance(chat_id)
            if check != False:
                msg = bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=texts.order_winthdraw.format(
                        chat_id, # user_id
                        check, # Сумма к выводу
                    )
                )

                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler(msg, order_winthdraw)
            else:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text='У вас нету средств на вывод!',
                )
        
        if call.data == 'exit_to_admin_menu':
            if func.check_admin(chat_id) == True:
                bot.send_message(
                    chat_id=chat_id,
                    text='🍒Привет, держи менюшку админа',
                    reply_markup=menu.admin_menu()
                )   

        if call.data == 'admin_info':
            if func.check_admin(chat_id) == True:
                info = func.admin_info()

                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=f'Пользователей за 1 час - {info[0]}\n'
                         f'Пользователей за 24 часа - {info[1]}\n'
                         f'Пользователей за 7 дней - {info[2]}\n'
                         f'Пользователей за все время - {info[3]}\n',
                    reply_markup=menu.back_to_admin_inline_menu()
                )
        
        if 'winthdraw_order_' in call.data:
            if func.check_admin(chat_id) == True:
                bot.send_message(
                    chat_id=chat_id,
                    text=func.winthdraw_order_info(call.data[16:]),
                    reply_markup=menu.del_winthdraw_order(call.data[16:])
                )

        if 'del_winthdraw_order_' in call.data:
            if func.check_admin(chat_id) == True:
                func.del_winthdraw_order(call.data[20:])
                bot.send_message(
                    chat_id=chat_id,
                    text='Запрос удален из бд'
                )

        if call.data == 'admin_winthdraw_orders':
            if func.check_admin(chat_id) == True:
                bot.send_message(
                    chat_id=chat_id,
                    text='Список запросов 👇',
                    reply_markup=func.winthdraw_order_list()
                )
                logging.info(f'Open ADNIM winthdraw list | {chat_id} | {func.get_date()}')

        if call.data == 'email_sending':
            if func.check_admin(chat_id) == True:
                msg = bot.send_message(
                    chat_id=chat_id,
                    text='Введите текст рассылки',
                    )
                
                bot.clear_step_handler_by_chat_id(chat_id)
                bot.register_next_step_handler(msg, admin_sending_messages)
        
        if call.data == 'exit_to_main_menu':
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text='Вы были возвращены в главное меню',
            )

        if call.data == 'bet_on_the_game':
            msg = bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=f'Ваш баланс - {func.check_user_balance(chat_id)}\n'
                     f'Мин. ставка 1р\n'
                     f'Введите сумму ставки',
            )

            bot.clear_step_handler_by_chat_id(chat_id)
            bot.register_next_step_handler(msg, bet_on_the_game)


    def bet_on_the_game(message):
        chat_id = message.chat.id

        try:
            if float(message.text) >= 1 and float(message.text) <= func.check_user_balance(chat_id):
                bet_dict = func.Bet_on_the_game(chat_id)
                func.bet_on_the_game_dict[chat_id] = bet_dict
                bet_dict = func.bet_on_the_game_dict[chat_id]
                bet_dict.bet = float(message.text)
                bet_dict.name = message.from_user.first_name

                msg = bot.send_message(
                    chat_id=chat_id,
                    text=f'Ваша ставка - {bet_dict.bet}\n'
                         'Для подтверждения отправть "Y"'
                )

                bot.register_next_step_handler(msg, bet_on_the_game2)
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text=f'На балансе недостатачно средств'
                )
        except:
            bot.send_message(
                    chat_id=chat_id,
                    text=f'Что-то пошло не по плану'
                )


    def bet_on_the_game2(message):
        chat_id = message.chat.id

        try:
            if message.text == "Y":
                bet_dict = func.bet_on_the_game_dict[chat_id]

                response = func.bet_on_the_game(bet_dict)

                msg = bot.send_message(
                    chat_id=chat_id,
                    text=response[0]
                )

                if func.check_bets_game(response[1]) == True:
                    print('TH START')
                    threading.Thread(target=start_game(), name='start_game')

            else:
                bot.send_message(
                    chat_id=chat_id,
                    text=f'Ставка отменена'
                )
        except Exception as e:
            bot.send_message(
                    chat_id=chat_id,
                    text=f'Что-то пошло не по плану'
                )


    def start_game():
        time.sleep(15)
        resp = func.start_game()
        try:
            bot.send_message(
                    chat_id=config.read_config('channel_id'),
                    text=f'🍀 Выиграл: {resp[0]}\n'
                         f'📊 Сумма выигрыша:{resp[1]}!\n'
                )
        except Exception as e:
            pass



    def order_winthdraw(message):
        chat_id = message.chat.id

        order = func.Order_winthdraw(chat_id)
        func.order_winthdraw_dict[chat_id] = order
        order = func.order_winthdraw_dict[chat_id]
        order.qiwi = message.text

        msg = bot.send_message(
            chat_id=chat_id,
            text=texts.order_winthdraw_2.format(
                chat_id,
                order.qiwi
            )
        )

        bot.register_next_step_handler(msg, order_winthdraw_2)

    
    def order_winthdraw_2(message):
        chat_id = message.chat.id
        order = func.order_winthdraw_dict[chat_id]
        order.code = random.randint(1111111111, 99999999999)

        if message.text == 'YES':
            func.order_winthdraw(order)

            try:
                bot.send_message(
                    chat_id=config.read_config('admin_id'),
                    text='⚠️ Создана заявка на вывод!'
                )
                logging.info(f'Winthdraw order | {chat_id} | {func.get_date()}')
            except: 
                pass

            bot.send_message(
                chat_id=chat_id,
                text=texts.order_winthdraw_3.format(
                    order.code,
                    order.qiwi
                    ),
                reply_markup=menu.back_to_main_inline_menu()
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text='Вы отменили создание заявки на вывод'
            )
    
    def admin_sending_messages(message):
        admin_sending = func.Admin_sending_messages(message.chat.id)
        func.admin_sending_messages_dict[message.chat.id] = admin_sending

        admin_sending = func.admin_sending_messages_dict[message.chat.id]
        admin_sending.text = message.text

        msg = bot.send_message(message.chat.id,
                               text='Отправьте "YES" для подтверждения')
        bot.register_next_step_handler(msg, admin_sending_messages_2)


    def admin_sending_messages_2(message):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()

        admin_sending = func.admin_sending_messages_dict[message.chat.id]

        if message.text == 'YES':
            cursor.execute(f'SELECT * FROM users')
            row = cursor.fetchall()
            start_time = time.time()
            amount_message = 0

            try:
                bot.send_message(config.read_config('admin_id'), f'❕ Вы запустили рассылку\n❕ Текст:\n\n{admin_sending.text}')
            except: pass

            for i in range(len(row)):
                try:
                    time.sleep(0.2)
                    bot.send_message(row[i][0], admin_sending.text)
                    amount_message += 1
                except:
                    pass
            
            sending_time = time.time() - start_time
            try:
                bot.send_message(config.read_config('admin_id'), f'❕ Рассылка закончена\n❕ Кол-во получателей - {amount_message}\n❕ Время выполнения рассылки - {sending_time} секунд')
            except: pass
        else:   
            bot.send_message(message.chat.id, text='Рассылка отменена', reply_markup=menu.admin_menu)
    
    
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(15)

