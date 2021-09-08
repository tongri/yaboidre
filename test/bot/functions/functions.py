import sqlite3
import random
import datetime
import requests
import json

import bot.settings.config as config
import bot.menu.bot_menu as menu

from bot.functions.logger import *

from telebot import types

check_payment_dict = {}
order_winthdraw_dict = {}
admin_sending_messages_dict = {}
bet_on_the_game_dict = {}

class Check_payment:
    def __init__(self, user_id):
        self.user_id = user_id
        self.code = None
        self.date = None
        self.markup = None


class Order_winthdraw:
    def __init__(self, user_id):
        self.user_id = user_id
        self.qiwi = None
        self.code = None


class Admin_sending_messages:
    def __init__(self, user_id):
        self.user_id = user_id
        self.text = None


class Bet_on_the_game:
    def __init__(self, user_id):
        self.user_id = user_id
        self.bet = None
        self.name = None


class Table_game:
    def __init__(self, user_id, start, end):
        self.user_id = user_id
        self.start = start
        self.end = end


def first_join(user_id, first_name, login):
    if check_user_in_bd(user_id) == False:
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()

        cursor.execute(f'INSERT INTO users VALUES("{user_id}", "{first_name}", "{login}", "{datetime.datetime.now()}", "0")')
        conn.commit()
    else:
        pass


def check_user_in_bd(user_id):
    logging.info(f'Run check_user_in_bd | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    check = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchall()

    if len(check) > 0:
        return True
    else:
        return False


def get_date():
    date = str(datetime.datetime.now())[:19]
    return date


def check_user_balance(user_id):
    logging.info(f'Run check_user_balance | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    check = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchall()

    if len(check) != 0:
        return float(check[0][4])
    else:
        return False


def check_game_info():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    info = cursor.execute(f'SELECT * FROM games').fetchall()

    all_bank = 0
    games = len(info)

    for i in info:
        all_bank = all_bank + float(i[1])

    
    return all_bank, games



def check_payment(user_id):
    logging.info(f'Run check_payment | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    try:
        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + config.read_config('qiwi_token')
        parameters = {'rows': '10'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(config.read_config('qiwi_number')),
            params=parameters)
        req = json.loads(h.text)
        result = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchone()
        comment = result[1]
        for i in range(len(req['data'])):
            if comment in str(req['data'][i]['comment']):
                    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

                    balance = float(balance[4]) + float(req["data"][i]["sum"]["amount"])

                    deposit = float(req["data"][i]["sum"]["amount"])

                    cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
                    conn.commit()

                    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                    conn.commit()

                    logging.info(f'Successful deposit | {user_id} | {get_date()}')

                    return True
    except:
        pass

    return False


def deposit_qiwi(user_id):
    logging.info(f'Run deposit_qiwi | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    code = random.randint(11111, 99999)

    check = cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}').fetchall()

    if len(check) > 0:
        cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
        conn.commit()

    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}")')
    conn.commit()


    url =  f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.read_config("qiwi_number")}&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&&blocked[0]=account&&blocked[1]=comment'

    markup = menu.payment_menu(url)

    return code, markup


def check_admin(user_id):
    logging.info(f'Run check_admin | {get_date()}')

    if str(user_id) in config.read_config('admin_id'):
        return True
    else:
        return False


def order_winthdraw(order):
    logging.info(f'Run order_winthdraw | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    winthdraw_sum = check_user_balance(order.user_id)

    cursor.execute(f'INSERT INTO order_winthdraw VALUES ("{order.user_id}", "{order.qiwi}", "{winthdraw_sum}", "{datetime.datetime.now()}", "{order.code}")')
    conn.commit()


def winthdraw_order_list():
    logging.info(f'Run winthdraw_order_list | {get_date()}')

    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    markup = types.InlineKeyboardMarkup(row_width=1)

    base = cursor.execute(f'SELECT * FROM order_winthdraw').fetchall()

    for i in base:
        markup.add(
            types.InlineKeyboardButton(text=f'{i[0]} | {i[2]} | {i[3]} | {i[1]}', callback_data=f'winthdraw_order_{i[4]}')
        )

    markup.add(
        types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_admin_menu')
    )

    return markup


def admin_info():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    date = datetime.datetime.now()

    h1 = 0
    h24 = 0
    d7 = 0
    all_time = 0

    users = cursor.execute(f'SELECT * FROM users').fetchall()

    for i in users:
        if date - datetime.timedelta(hours=1) <= datetime.datetime.fromisoformat(i[3]):
            h1 += 1
        if date - datetime.timedelta(hours=24) <= datetime.datetime.fromisoformat(i[3]):
            h24 += 1
        if date - datetime.timedelta(days=7) <= datetime.datetime.fromisoformat(i[3]):
            d7 += 1
    
    all_time = len(users)

    return h1, h24, d7, all_time


def get_info_active_game():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    active_game = cursor.execute(f'SELECT * FROM active_game').fetchall()

    if len(active_game) == 0:
        active_game = create_game()
    else:
        active_game = active_game[0][0]

    game = cursor.execute(f'SELECT * FROM GAME_{active_game}').fetchall()

    if len(game) == 0:
        return 0, 0, active_game # bank, bets, game_id
    else:
        bank = 0
        bets = 0

        for i in game:
            bank = bank + float(i[1])
            bets += 1
        
        return bank, bets, active_game


def create_game():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    id_game = random.randint(1111111, 9999999)
    date = datetime.datetime.now()

    cursor.execute(f'INSERT INTO active_game VALUES ("{id_game}", "{date}", "0")')
    conn.commit()

    conn.execute(f"CREATE TABLE 'GAME_{id_game}' (user_id text, bet text, date text, name text)")

    return id_game


def bet_on_the_game(bet_dict):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    active_game_id = get_id_active_game()

    status = 'Ставка не была сделана'

    bets = 0

    try:
        check = cursor.execute(f'SELECT * FROM "GAME_{active_game_id}" WHERE user_id = "{bet_dict.user_id}"').fetchall()

        if len(check) == 0:
            cursor.execute(f'INSERT INTO "GAME_{active_game_id}" VALUES ("{bet_dict.user_id}", "{bet_dict.bet}", "{datetime.datetime.now()}", "{bet_dict.name}")')
            conn.commit()
        else:
            balance = float(check[0][1]) + float(bet_dict.bet)
            cursor.execute(f'UPDATE "GAME_{active_game_id}" SET bet = {balance} WHERE user_id = "{bet_dict.user_id}"')
            conn.commit()

        update_user_balance(str(bet_dict.user_id), -bet_dict.bet)

        status = 'Ставка успешна сделана'

        bets = len(cursor.execute(f'SELECT * FROM "GAME_{active_game_id}"').fetchall())

    except Exception as e:
        print(e)

    return status, bets
        


def get_id_active_game():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    active_game = cursor.execute(f'SELECT * FROM active_game').fetchall()

    if len(active_game) == 0:
        active_game = create_game()
        return active_game
    else:
        active_game = active_game[0][0]
        return active_game


def update_user_balance(user_id, value):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    balance = cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"').fetchone()

    balance = float(balance[4]) + float(value)

    cursor.execute(f'UPDATE users SET balance = {balance} WHERE user_id = "{user_id}"')
    conn.commit()


def check_bets_game(bets):
    if int(bets) == 2:
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()

        check = cursor.execute(f'SELECT * FROM active_game').fetchone()
        if int(check[2]) == 0:
            cursor.execute(f'UPDATE active_game SET status = 1')
            conn.commit()
            return True
        else:
            return False
    else:
        return False


def start_game():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    active_game_id = get_id_active_game()

    game = cursor.execute(f'SELECT * FROM "GAME_{active_game_id}"').fetchall()

    bank = 0
    for i in game:
        bank = bank + float(game[0][1])

    bank_win = (bank / 100) * (100 - int(config.read_config("percent_admin")))

    table = {} #{'id': ['0', '10']}

    last = 0

    for i in game: # user_id text, bet text, date text
        tb = Table_game(i[0], last, float(i[1]) * 100 )
        last += float(i[1]) * 100 + 1
        table[i[0]] = tb

    win = random.randint(0, last)
    
    for i in game:
        tb = table[i[0]]
        if win >= tb.start and win <= tb.end:
            win = table[i[0]].user_id
            update_user_balance(win, bank_win)
            add_log_games(win, bank, active_game_id)
            del_active_game()
            
            return win, bank_win


def add_log_games(win, bank, active_game_id):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO games VALUES ("{win}", "{bank}", "{active_game_id}", "{datetime.datetime.now()}")')
    conn.commit()


def del_active_game():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()
    
    cursor.execute(f'DELETE FROM active_game')
    conn.commit()


def check_bets_for_info():
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    active_game_id = get_id_active_game()

    game = cursor.execute(f'SELECT * FROM "GAME_{active_game_id}"').fetchall()

    bank = 0
    for i in game:
        bank = bank + float(game[0][1])

    try:
        percent_1 = 100 / bank

        info = ''   # user_id/bet/win rate

        for i in game: # user_id text, bet text, date text
            info = info + f'{i[3]} | {i[1]} | {float("{:.3f}".format(float(i[1])*percent_1))} %\n'
        
        return info
    except:
        return ''


def winthdraw_order_info(code):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    info = cursor.execute(f'SELECT * FROM order_winthdraw WHERE id = "{code}"').fetchone()

    msg = f'ID - {info[4]}\n' \
          f'user_id - {info[0]}\n' \
          f'Сумма - {info[2]}\n' \
          f'QIWI - {info[1]}\n' \
          f'Дата создания запроса - {info[3]}\n'

    return msg


def del_winthdraw_order(code):
    conn = sqlite3.connect('base.db')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM order_winthdraw WHERE id = "{code}"')
    conn.commit()