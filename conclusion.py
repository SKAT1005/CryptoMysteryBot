import decimal
import os

import django
from telebot import types

import buttons
from const import bot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, AdminMessage, History


def delite_for_admins(id):
    """Удаление всех сообщений админам"""
    admin_messages = AdminMessage.objects.get(id=id)
    for message_id in admin_messages.messages_id.split(','):
        try:
            bot.delete_message(chat_id=admin_messages.chat_id, message_id=message_id)
        except Exception:
            pass
    admin_messages.delete()

def history(type, send_value, send_cripto, user_id, wallet):
    user = User.objects.get(chat_id=user_id)
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_cripto=send_cripto,
    )
def approve_conclusion(data):
    cripto = data[0]
    id = data[1]
    user = User.objects.get(chat_id=data[2])
    delite_for_admins(id=id)
    user.wallet.delite_cripto(cripto=cripto, value=user.send_cripto)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на вывод {user.send_cripto} {cripto} одобрена!')
    history(type='Вывод', send_value=user.send_cripto, send_cripto=cripto, wallet=data[-1])
    user.send_cripto = 0
    user.save()


def cansel_conclusion(data):
    cripto = data[0]
    id = data[1]
    user = User.objects.get(chat_id=data[2])
    delite_for_admins(id=id)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на вывод {user.send_cripto} {cripto} отклонена!')
    user.send_cripto = 0
    user.save()


def send_to_admin(chat_id, data, user):
    cripto = data[0]
    value = str(decimal.Decimal(float(data[1].replace(',', '.')) * 0.95)).replace('.', ',')
    wallet = data[2]
    admin_message = AdminMessage.objects.create(chat_id=chat_id)
    admins = User.objects.filter(is_admin=True)
    markup = buttons.admins_button(cripto=cripto, user_id=chat_id, id=admin_message.id, wallet=wallet)
    text = 'ВЫВОД СРЕДСТВ:\n' \
           f'Пользователь: {user.chat_id}\n' \
           f'Выводит: *{value}* {cripto}\n' \
           f'Номер кошелек\карта: `{wallet}`\n\n' \
           f'БАЛАННС ПОЛЬЗОВАТЕЛЯ:\n' + user.wallet.wallet_balance()
    messages_id = ''
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup, parse_mode='MarkdownV2')
            messages_id += f'{msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()


def validate_user_wallet_input(message, chat_id, cripto, value, user, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    text = 'ИНФОРМАЦИЯ О ВЫВОДЕ:\n' \
           f'Вы выводите: {value} {cripto}\n' \
           f'Номер кошелька\карты для вывода: {message.text}'
    bot.send_message(chat_id=chat_id, text=text,
                     reply_markup=buttons.conclusion_button(cripto=cripto, value=value, wallet=message.text))


def user_wallet_input(chat_id, user, cripto, value, error=''):
    if error:
        text = error
    else:
        text = 'Введите кошелек/номер карты, на который хотите вывести'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_to_menu())
    bot.register_next_step_handler(msg, validate_user_wallet_input, chat_id, cripto, value, user, msg.id)


def validate_cripto_input(message, chat_id, message_id, cripto, user):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    try:
        value = decimal.Decimal(message.text.replace(',', '.'))
        if value <= 0:
            raise Exception
    except Exception:
        error = 'Введите число, которое больше 0'
        input_cripto_text(chat_id=chat_id, cripto=cripto, error=error)
    else:
        if user.wallet.check_balance(cripto=cripto, value=value):
            user.send_cripto = value
            user.save()
            user_wallet_input(chat_id=chat_id, user=user, cripto=cripto, value=value)


def input_cripto_text(chat_id, cripto, user, error=''):
    if error:
        text = error
    else:
        text = 'Введите сколько валюты вы хотете вывести'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_to_menu())
    bot.register_next_step_handler(msg, validate_cripto_input, chat_id, msg.id, cripto, user)


def callback(data, user, chat_id):
    if len(data) == 0:
        bot.send_message(chat_id=chat_id, text='Выберите криптовалюту для перевода',
                         reply_markup=buttons.choose_cripto(param='conclusion'))
    elif len(data) == 1:
        input_cripto_text(chat_id=chat_id, cripto=data[0], user=user)
    elif data[0] == 'approve':
        approve_conclusion(data=data[1:])
    elif data[0] == 'cansel':
        cansel_conclusion(data=data[1:])
    else:
        send_to_admin(chat_id=chat_id, user=user, data=data)
