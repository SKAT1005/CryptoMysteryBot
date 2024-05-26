import os

import django
import requests

import buttons
import conclusion
import history
import review
import send_to_user
from const import bot
import change_and_buy

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, Wallet


def menu(chat_id):
    text = 'Текст главного меню'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.menu_buttons())


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if not User.objects.filter(chat_id=chat_id):
        wallte = Wallet.objects.create()
        user, _ = User.objects.create(chat_id=chat_id, wallet=wallte), True
    else:
        user, _ = User.objects.get(chat_id=chat_id), False
    if _ or not user.referal_id:
        ref_id = message.text.split()
        if len(ref_id) > 1 and User.objects.filter(chat_id=ref_id[1]) and ref_id[1] != str(chat_id):
            user.referal_id = ref_id[1]
            user.save()
    menu(chat_id=chat_id)


def wallet(chat_id, user):
    text = f'ID вашего кошелька: `{chat_id}`\n' \
           f'Баланс вашего кошелька:\n\n' + user.wallet.wallet_balance()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.wallet_buttons(chat_id), parse_mode='MarkdownV2')


def get_course(cripto):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={cripto}&tsyms=RUB'
    response = requests.get(url).json()
    return response['RUB']


def course(chat_id):
    msg = bot.send_message(chat_id=chat_id, text='Подождите, пожалуйста. Мы ищем самый актуальный курс')
    ciptos = ['BTC', 'ETH', 'USDT', 'TRX', 'TON', 'XMR']
    text = 'Текущие курсы криптовалют\n\n'
    for cripto in ciptos:
        course = get_course(cripto=cripto)
        text += f'RUB -> {cripto}: {course}\n'
    bot.edit_message_text(chat_id=chat_id, text=text, message_id=msg.id, reply_markup=buttons.go_to_menu())


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    user, _ = User.objects.get_or_create(chat_id=call.from_user.id)
    if call.message:
        data = call.data.split('|')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception:
            pass
        if data[0] == 'menu':
            user.send_cripto = 0
            user.get_cripto = 0
            user.save()
            menu(chat_id=chat_id)

        elif data[0] == 'change':
            change_and_buy.new_callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'my_wallet':
            wallet(chat_id=chat_id, user=user)
        elif data[0] == 'send_to_user':
            send_to_user.callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'conclusion':
            conclusion.callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'course':
            course(chat_id=chat_id)
        elif data[0] == 'review':
            review.callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'history':
            history.history(user)
        else:
            menu(chat_id=chat_id)


bot.polling(none_stop=True)
