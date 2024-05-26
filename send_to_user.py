import decimal
import os

import django

import buttons
from const import bot
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, History


def history(type, send_value, send_cripto, from_user_id, to_user_id):
    user = User.objects.get(chat_id=from_user_id)
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_cripto=send_cripto,
        address=to_user_id
    )
def send_to_user(chat_id, data, user):
    cripto = data[0]
    to_user_id = data[1]
    to_user = User.objects.get(chat_id=to_user_id)
    value = user.send_cripto
    history(type='Перевод пользователю', send_value=value, send_cripto=cripto, from_user_id=chat_id, to_user_id=to_user_id)
    user.wallet.delite_cripto(cripto=cripto, value=value)
    user.send_cripto = 0
    user.save()
    to_user.wallet.buy(cripto=cripto, value=value)
    to_user.save()
    bot.send_message(chat_id=chat_id, text='Перевод прошел успешно', reply_markup=buttons.go_to_menu())
    bot.send_message(chat_id=to_user.chat_id, text=f'Вам отправили {value} {cripto}')



def validate_user_wallet_input(message, chat_id, cripto, value, user, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    user_id = message.text
    if User.objects.filter(chat_id=user_id):
        text = 'ИНФОРМАЦИЯ О ПЕРЕВОДЕ:\n' \
               f'Вы отправляете: {value} {cripto}\n' \
               f'Кому отправляете: {user_id}'
        bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.send_to_user_button(cripto=cripto, user_id=user_id))
    else:
        user_vallet_input(chat_id=chat_id, user=user, cripto=cripto, value=value, error='Данного пользователя нет в боте')




def user_wallet_input(chat_id, user, cripto, value, error=''):
    if error:
        text = error
    else:
        text = 'Введите ID кошелька пользователя, которому хотите перевести средства'
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
        text = 'Введите сколько валюты вы хотете перевести'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_to_menu())
    bot.register_next_step_handler(msg, validate_cripto_input, chat_id, msg.id, cripto, user)

def callback(data, user, chat_id):
    if len(data) == 0:
        bot.send_message(chat_id=chat_id, text='Выберите криптовалюту для перевода', reply_markup=buttons.choose_cripto(param='send_to_user'))
    elif len(data) == 1:
        input_cripto_text(chat_id=chat_id, cripto=data[0], user=user)
    else:
        send_to_user(chat_id=chat_id, user=user, data=data)
