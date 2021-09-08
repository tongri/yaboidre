
from telebot import types

import bot.menu.names_btns_menu as names_btns
import bot.settings.config as config


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        names_btns.main_menu[0], # 🎲 Рулетка
        names_btns.main_menu[1], # 👤 Мой профиль
        names_btns.main_menu[2], # 🚀 О проекте
    )
    
    return markup


def info_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='🗨 Чат', url=config.read_config('chat')),
        types.InlineKeyboardButton(text='🛠 Поддержка', url=config.read_config('support')),
        types.InlineKeyboardButton(text='👁 Смотреть результаты', url=config.read_config('results')),
    )

    return markup


def profile_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='⚜️ Пополнить баланс', callback_data='deposit'),
        types.InlineKeyboardButton(text='⚜️ Вывод средст', callback_data='winthdraw'),
    )

    return markup


def admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='❕ Информация о боте', callback_data='admin_info'),
        types.InlineKeyboardButton(text='❕ Запросы на вывод', callback_data='admin_winthdraw_orders'),
        types.InlineKeyboardButton(text='❕ Рассылка', callback_data='email_sending'),
    )

    return markup


def payment_menu(url):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Перейти к оплате', url=url),
    )
    markup.add(
        types.InlineKeyboardButton(text='Проверить', callback_data='check_payment'),
        types.InlineKeyboardButton(text='Отменить оплату', callback_data='exit_to_main_menu'),
    )

    return markup


def back_to_main_inline_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Выйти в главное меню', callback_data='exit_to_main_menu')
    )

    return markup


def back_to_admin_inline_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_admin_menu')
    )

    return markup


def game_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='💰 Сделать ставку', callback_data='bet_on_the_game'),
        types.InlineKeyboardButton(text='🔙 Выйти', callback_data='exit_to_main_menu')
    )

    return markup


def del_winthdraw_order(code):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Удалить из бд', callback_data=f'del_winthdraw_order_{code}'),
        types.InlineKeyboardButton(text='Выйти', callback_data='exit_to_admin_menu')
    )

    return markup