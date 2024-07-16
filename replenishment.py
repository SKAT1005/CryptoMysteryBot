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
from change_and_buy import payment
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

def get_course(cripto, value='RUB'):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={cripto}&tsyms={value}'
    response = requests.get(url).json()
    return response[value]
def history(type, send_value, send_cripto, get_value, get_cripto, user):
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_cripto=send_cripto,
        get_value=get_value,
        get_cripto=get_cripto,
        course=get_course(send_cripto)
    )


def approve_replenishment(data, msg_text):
    cripto = data[1]
    id = data[2]
    user = User.objects.get(chat_id=data[3])
    # delite_for_admins(id=id, msg_text=msg_text, type='❌')
    user.wallet.buy(cripto=cripto, value=user.send_cripto)
    number_str = get_number(user.send_cripto)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на пополнение {number_str} {cripto} одобрена! Оставьте отзыв и получите 1 USDT', reply_markup=buttons.review())
    history(type='Пополнения', send_value=user.send_cripto, send_cripto=cripto, get_cripto=cripto, get_value=user.send_cripto, user=user)
    user.send_cripto = 0
    user.save()


def cansel_replenishment(data, msg_text):
    cripto = data[1]
    id = data[2]
    user = User.objects.get(chat_id=data[3])
    # delite_for_admins(id=id, msg_text=msg_text, type='❌')
    number_str = get_number(user.send_cripto)
    bot.send_message(chat_id=user.chat_id, text=f'Ваша заявка на вывод {number_str} {cripto} отклонена!')
    user.send_cripto = 0
    user.save()

def admins_buttons(chat_id, cripto, id):
    """Кнопки для админов"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить', callback_data=f'replenishment|adm_approve|{cripto}|{id}|{chat_id}')
    cansel = types.InlineKeyboardButton(text='Отклонить', callback_data=f'replenishment|adm_cansel|{cripto}|{id}|{chat_id}')
    view_user = types.InlineKeyboardButton('Посмотерь аккаунт пользователя', url=f'tg://user?id={chat_id}')
    markup.add(approve, cansel, view_user)
    return markup

def send_to_admin(chat_id, data, user):
    admin_message = AdminMessage.objects.create(chat_id=chat_id)
    admins = User.objects.filter(is_admin=True)
    cripto = data[1]
    value = str(user.send_cripto).replace('.', ',')
    markup = admins_buttons(chat_id=chat_id, cripto=cripto, id=admin_message.id)
    text = 'ПОПОЛНЕНИЕ СЧЕТА:\n' \
           f'Пользователь: {user.chat_id}\n' \
           f'Сумма пополнения: *{value}* {cripto}\n\n' \
           f'*БАЛАННС ПОЛЬЗОВАТЕЛЯ:*\n' + user.wallet.wallet_balance()
    messages_id = ''
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup, parse_mode='MarkdownV2')
            messages_id += f'{msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()


def input_cripto_text(chat_id, cripto, user, error=''):
    if error:
        text = error
    else:
        text = 'Введите сколько валюты вы хотете пополнить'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_to_menu())
    bot.register_next_step_handler(msg, validate_cripto_input, chat_id, msg.id, cripto, user)


def choose_net(chat_id, data):
    text = f'Выберите способ пополнения.'
    markup = types.InlineKeyboardMarkup(row_width=3)
    back = types.InlineKeyboardButton(text='Назад', callback_data=f'replenishment')
    if data[0] == 'RUB':
        sber = types.InlineKeyboardButton(text='Сбербанк', callback_data=f'replenishment|{data[0]}|sber')
        # tink = types.InlineKeyboardButton(text='Тинькофф', callback_data=f'replenishment|{data[0]}|tink')
        gpb = types.InlineKeyboardButton(text='ГПБ', callback_data=f'replenishment|{data[0]}|gpb')
        psb = types.InlineKeyboardButton(text='ПСБ', callback_data=f'replenishment|{data[0]}|psb')
        alpha = types.InlineKeyboardButton(text='Альфа Банк', callback_data=f'replenishment|{data[0]}|alpha')
        markup.add(sber, gpb, psb, alpha)
    else:
        trc20 = types.InlineKeyboardButton(text='TRC20', callback_data=f'replenishment|{data[0]}|TRC20')
        erc20 = types.InlineKeyboardButton(text='ERC20', callback_data=f'replenishment|{data[0]}|ERC20')
        bep20 = types.InlineKeyboardButton(text='BEP20', callback_data=f'replenishment|{data[0]}|BEP20')
        spl = types.InlineKeyboardButton(text='SPL', callback_data=f'replenishment|{data[0]}|SPL')
        markup.add(trc20, erc20, bep20, spl)
    markup.add(back)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def validate_cripto_input(message, chat_id, message_id, data):
    user = User.objects.get(chat_id=chat_id)
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
        input_value(chat_id=chat_id, data=data, error=error)
    else:
        markup = types.InlineKeyboardMarkup()
        user.send_cripto = value
        user.save()
        if data[0] in ['RUB', 'USDT']:
            back = types.InlineKeyboardButton('Назад', callback_data=f'replenishment|{data[0]}|{data[1]}')
            acept = types.InlineKeyboardButton('✅ Зафиксировать ✅',
                                               callback_data=f'replenishment|accept|{data[0]}|{data[1]}')
        else:
            acept = types.InlineKeyboardButton('✅ Зафиксировать ✅',
                                               callback_data=f'replenishment|accept|{data[0]}')
            back = types.InlineKeyboardButton('Назад', callback_data=f'replenishment|{data[0]}')
        markup.add(acept, back)
        text = '📥 Вы отдаёте:\n\n' \
               f'{data[0]}: {value}'
        bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def send_wallet(chat_id, user, data):
    value = str(user.send_cripto).replace('.', ',')
    if data[1] in ['USDT', "RUB"]:
        wallet = payment[data[1]][data[2]]
        text =f'Отправьте {value} {data[1]} на \n\n' \
               f'{wallet}'
        if data[1] == 'RUB':
            text += f'\n\nПросим обратить внимание на правила работы нашего сервиса:\n' \
                    f'1\. Перевод может быть осуществлен только с личной карты\.\n' \
                    f'2\. После совершения перевода перешлите чек в данный чат\.\n' \
                    f'3\. Совершайте перевод исключительно на указанную сумму для каждых реквизитов из списка ниже\.\n'
    else:
        wallet = payment[data[1]]
        text = f'Отправьте {value} {data[1]} на \n\n' \
               f'{wallet}'
    markup = types.InlineKeyboardMarkup()
    send = types.InlineKeyboardButton(text='✅Отправил✅', callback_data=f'replenishment|send|{data[1]}')
    cansel = types.InlineKeyboardButton(text='❌Отменить❌', callback_data='menu')
    markup.add(send, cansel)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup, parse_mode='MarkdownV2')


def input_value(chat_id, data, error=None):
    if error:
        text = error
    else:
        text = 'Введите сумму пополнения'
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton('Назад', callback_data=f'replenishment{data[0]}')
    markup.add(back)
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    bot.register_next_step_handler(msg, validate_cripto_input, chat_id, msg.id, data)


def callback(data, user, chat_id, msg_text=None):
    if len(data) == 0:
        bot.send_message(chat_id=chat_id, text='Выберите криптовалюту для пополнения',
                         reply_markup=buttons.choose_cripto(param='replenishment'))
    elif data[0] == 'accept':
        send_wallet(chat_id=chat_id, data=data, user=user)
    elif data[0] == 'send':
        bot.send_message(chat_id=chat_id, text='🧿Crypto Mystery пополнит ваш баланс при зачислении средств💸')
        send_to_admin(chat_id=chat_id, data=data, user=user)
    elif data[0] == 'adm_approve':
        approve_replenishment(data, msg_text=msg_text)
    elif data[0] == 'adm_cansel':
        cansel_replenishment(data=data, msg_text=msg_text)
    elif len(data) == 1:
        if data[0] in ['RUB', 'USDT']:
            choose_net(chat_id, data)
        else:
            input_value(chat_id=chat_id, data=data)
    elif len(data) == 2:
        if data[0] in ['RUB', 'USDT']:
            input_value(chat_id=chat_id, data=data)

