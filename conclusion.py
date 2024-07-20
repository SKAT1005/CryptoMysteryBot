import decimal
import os

import django
import requests
from telebot import types

import buttons
from const import bot
from change_and_buy import get_number

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, AdminMessage, History


def delite_for_admins(id, msg_text, type):
    """Удаление всех сообщений админам"""
    msg_text = type + msg_text
    admin_messages = AdminMessage.objects.filter(id=id)
    if admin_messages:
        for message_id in admin_messages[0].messages_id.split(','):
            chat_id, msg_id = message_id.split()
            try:
                bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=msg_text)
            except Exception:
                pass
        admin_messages[0].delete()
def get_course(cripto, value='USDT'):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={cripto}&tsyms={value}'
    response = requests.get(url).json()
    return response[value]
def history(type, send_value, send_cripto, user_id, wallet):
    user = User.objects.get(chat_id=user_id)
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_cripto=send_cripto,
        address=wallet,
        course_send=get_course(send_cripto)
    )
def approve_conclusion(data, msg_text):
    cripto = data[0]
    id = data[1]
    user = User.objects.get(chat_id=data[2])
    # delite_for_admins(id=id, msg_text=msg_text, type='👌\n')
    user.wallet.delite_cripto(cripto=cripto, value=user.send_cripto)
    number_str = get_number(user.send_cripto)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на вывод {number_str} {cripto} одобрена!Оставьте отзыв и получите 1 USDT', reply_markup=buttons.review())
    history(type='Вывод', send_value=user.send_cripto, send_cripto=cripto, wallet=data[-1], user_id=data[-2])
    user.send_cripto = 0
    user.save()


def cansel_conclusion(data, msg_text):
    cripto = data[0]
    id = data[1]
    user = User.objects.get(chat_id=data[2])
    # delite_for_admins(id=id, msg_text=msg_text, type='👌\n')
    number_str = get_number(user.send_cripto)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на вывод {number_str} {cripto} отклонена!')
    user.send_cripto = 0
    user.save()


def send_to_admin(chat_id, data, user):
    cripto = data[0]
    value = str(decimal.Decimal(round(float(data[1].replace(',', '.')) * 0.95, 2))).replace('.', ',')
    wallet = data[2]
    admin_message = AdminMessage.objects.create(chat_id=chat_id)
    admins = User.objects.filter(is_admin=True)
    net = ''
    if cripto in ['USDT', 'RUB']:
        net = f'Банк/Сеть: {data[-1]}\n'
    markup = buttons.admins_button(cripto=cripto, user_id=chat_id, id=admin_message.id, wallet=wallet)
    number_str = value
    text = 'ВЫВОД СРЕДСТВ:\n' \
           f'Пользователь: {user.chat_id}\n' \
           f'Выводит: *{number_str}* {cripto}\n' \
           f'{net}' \
           f'Номер кошелек\карта: `{wallet}`\n\n' \
           f'БАЛАННС ПОЛЬЗОВАТЕЛЯ:\n' + user.wallet.wallet_balance()
    messages_id = ''
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup, parse_mode='MarkdownV2')
            messages_id += f'{admin.chat_id} {msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()

def choose_bank_or_net(message, chat_id, cripto, value, user, wallet, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    number_str = get_number(value)
    text = 'ИНФОРМАЦИЯ О ВЫВОДЕ:\n' \
           f'Вы выводите: {number_str} {cripto}\n' \
           f'Номер кошелька\карты для вывода: {wallet}\n' \
           f'Банк\Сеть: {message.text}\n\n' \
           f'===================================\n' \
           'Баланс вашего кошелька:\n\n' + user.wallet.wallet_balance()
    bot.send_message(chat_id=chat_id, text=text,
                     reply_markup=buttons.conclusion_button(cripto=cripto, value=value, wallet=wallet, net=message.text))
def validate_user_wallet_input(message, chat_id, cripto, value, user, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    number_str = get_number(value)
    if cripto in ['USDT', "RUB"]:
        msg = bot.send_message(chat_id, text='Выберите сеть/банк, на который вы хортите вывести средства', reply_markup=buttons.choose_bank_or_net(cripto))
        bot.register_next_step_handler(msg, choose_bank_or_net, chat_id, cripto, value, user, message.text, msg.id)
    else:
        text = 'ИНФОРМАЦИЯ О ВЫВОДЕ:\n' \
               f'Вы выводите: {number_str} {cripto}\n' \
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
            error = 'Введите число, которое больше 0\n\n'
            raise Exception
        if not user.wallet.check_balance(cripto, value):
            error = 'На вашем балансе недостаточно средств\n\n'
            raise Exception
    except Exception:
        input_cripto_text(chat_id=chat_id, cripto=cripto, user=user, error=error)
    else:
        if user.wallet.get_balance(cripto=cripto):
            user.send_cripto = value
            user.save()
            user_wallet_input(chat_id=chat_id, user=user, cripto=cripto, value=value)


def input_cripto_text(chat_id, cripto, user, error=''):
    if error:
        text = error + f'===================================\n' \
               f'Баланс вашего кошелька: {user.wallet.balance(cripto)} {cripto}'
    else:
        text = 'Введите сколько валюты вы хотете вывести\n\n' \
               f'===================================\n' \
               f'Баланс вашего кошелька: {user.wallet.balance(cripto)} {cripto}'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.conclusion(cripto))
    bot.register_next_step_handler(msg, validate_cripto_input, chat_id, msg.id, cripto, user)


def callback(data, user, chat_id, msg_text=None):
    if len(data) == 0:
        bot.send_message(chat_id=chat_id, text='Выберите криптовалюту для перевода',
                         reply_markup=buttons.choose_cripto(param='conclusion'))
    elif len(data) == 1:
        input_cripto_text(chat_id=chat_id, cripto=data[0], user=user)
    elif len(data) == 2:
        value = user.wallet.get_balance(data[0])
        if int(value) <= 0:
            bot.send_message(chat_id=chat_id, text='Вы не можете вывести эту валюту т.к ваш баланс слишком маленький', reply_markup=buttons.go_to_wallet())
        else:
            user.send_cripto = value
            user.save()
            user_wallet_input(chat_id=chat_id, user=user, cripto=data[0], value=value)
    elif data[0] == 'approve':
        approve_conclusion(data=data[1:], msg_text=msg_text)
    elif data[0] == 'cansel':
        cansel_conclusion(data=data[1:], msg_text=msg_text)
    else:
        send_to_admin(chat_id=chat_id, user=user, data=data)
