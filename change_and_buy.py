import datetime
import decimal
import os

import django
import requests
from telebot import TeleBot, types

import buttons

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from const import bot
from app.models import User, AdminMessage, History

payment = {
    'RUB': {
        'sber': "🏦 Банк: Сбербанк:\n"
                "💳 Номер карты: `2202 2018 2009 8511`\n"
                "👤 Инициалы: *Ярослав Олегович К*",
        'tink': "🏦 Банк: *Тинькофф*\n"
                "💳 Номер карты: `000000000000000`\n"
                "👤 Инициалы: *Ярослав Олегович К*",
        'city': "🏦 Банк: *Сити*\n"
                "💳 Номер карты: `5318 0949 3544 4413`\n"
                "👤 Инициалы: *Ярослав Олегович К*",
        'gpb': "🏦 Банк: *ГПБ*\n"
               "💳 Номер карты: `2200 0117 0356 0327`\n"
               "👤 Инициалы: *Ярослав Олегович К*",
        'psb': "🏦 Банк: *ПСБ*\n"
               "💳 Номер карты: `5586 7260 9690 8489`\n"
               "👤 Инициалы: *Ярослав Олегович К*",
        'alpha': "🏦 Банк: *Альфа банк*\n"
                 "💳 Номер карты: `2200 1532 4224 4574`\n"
                 "👤 Инициалы: *Ярослав Олегович К*",
    },

    'USDT': {
        "TRC20": "`TGnUndFN5BDhjesFVTjFKWFojWVfg5CiZa`\n",
        "ERC20": "`0xAF440D7449C33E2CE778498D89261EaD9aa15636`\n",
        "BEP20": "`0xAF440D7449C33E2CE778498D89261EaD9aa15636`\n",
        "SPL": "`7KT9Tr8TgrUAeGthWznmxTfVpnhZdyVCfJUmEPGyxq4q`\n",
    },
    'ETH': '`0xAF440D7449C33E2CE778498D89261EaD9aa15636`',
    'BTC': '`bc1qctuy4vkdrfs63w6dth0qmnpplqpa8nrkaj65zp`',
    'XMR': '`43UdM7hT3TXHhG7rtceut6KYso8VCeMxiB87doc9AVuG9Gm1jDa1XpmcXM8tF2VxxdFU6VZsHnZX7fHvaH8bBfejP2tL9GS`',
    'TON': '`EQAwPATVIhHQrpMkGkAaLHvVanhhoF80HRkqGELD4-jENteG`',
    'TRX': '`TGnUndFN5BDhjesFVTjFKWFojWVfg5CiZa`'

}
def history(type, send_value, send_cripto, get_value, get_cripto, user_id):
    course = get_course(send_cripto, get_cripto)
    user = User.objects.get(chat_id=user_id)
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_cripto=send_cripto,
        get_value=get_value,
        get_cripto=get_cripto,
        course=course
    )

def admins_buttons(chat_id, data, id):
    """Кнопки для админов"""
    inline = f"{data[0]}|{data[1]}|{data[2]}"
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить', callback_data=f'change|adm_approve|{inline}|{id}|{chat_id}')
    cansel = types.InlineKeyboardButton(text='Отклонить', callback_data=f'change|adm_cansel|{id}|{chat_id}')
    markup.add(approve, cansel)
    return markup


def send_message_to_admin(data, chat_id):
    """Отправка сообщений админам"""
    admin_message = AdminMessage.objects.create(chat_id=chat_id)
    markup = admins_buttons(chat_id=chat_id, data=data, id=admin_message.id)
    send_cur = data[1]  # Валюту, которую отдаем
    get_cur = data[2]  # Валюта, которую получаем
    admins = User.objects.filter(is_admin=True)
    user = User.objects.get(chat_id=chat_id)
    send_value = get_number(user.send_cripto)
    get_value = get_number(user.get_cripto)
    if data[0] == 'confirm':
        text = "ВНУТРЕННИЙ ОБМЕН\n\n" + \
               f"Отдает {send_value} - {send_cur} \n\n" + \
               f"Получает{get_value} - {get_cur}\n\n" + user.wallet.wallet_balance()
    else:
        bot.send_message(chat_id=chat_id, text='🧿Crypto Mystery пополнит ваш баланс при зачислении средств💸')
        text = 'ВНЕШНИЙ ОБМЕН\n\n' \
               f'Отдает: {send_value} - {send_cur}\n' \
               f'Получает: {get_value} - {get_cur}\n'
    messages_id = ''
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup)
            messages_id += f'{admin.id} {msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()

def check_referal(user, cripto, value):
    if user.referal_id:
        referal = User.objects.get(chat_id=user.referal_id)
        referal.wallet.buy(cripto, value)
        referal.save()
        number_str = get_number(value)
        bot.send_message(chat_id=referal.chat_id, text=f'Ваш баланс был пополнен на {number_str} {cripto}, благодаря вашему рефералу')


def admin_approve(data):
    """Если админ подтверждает действие"""
    user = User.objects.get(chat_id=data[-1])
    check_referal(user, data[3], decimal.Decimal(float(data[5].replace(',', '.'))*0.1))
    if data[1] == 'confirm':
        type = 'Обмен'
        first_value = user.send_cripto
        second_value = user.get_cripto
        user.wallet.change(data[2], first_value, data[3], second_value)
    else:
        type = 'Пополнение'
        value = user.get_cripto
        user.wallet.buy(data[3], value)
    try:
        user.last_value = f'{user.get_cripto} {data[3]}'
        user.save()
        number_str = get_number(user.get_cripto)
        bot.send_message(chat_id=data[-1], text=f'Ваш счет успешно пополнен на {number_str} {data[3]}\n'
                                                f'Оставьте отзыв и получите 1 USDT на ваш счет', reply_markup=buttons.review())
    except Exception:
        pass
    history(type=type, send_value=user.send_cripto, send_cripto=data[2], get_value=user.get_cripto, get_cripto=data[3], user_id=data[-1])
    user.send_cripto = 0
    user.save()


def admin_cansel(data):
    """Если админ отклоняет действие"""
    user = User.objects.get(id=data[-1])
    user.get_cripto = 0
    user.send_cripto = 0
    user.save()
    try:
        bot.send_message(chat_id=data[-1], text=f'Вам отказано в пополнении счета')
    except Exception:
        pass


def delite_for_admins(id):
    """Удаление всех сообщений админам"""
    admin_messages = AdminMessage.objects.filter(id=id)
    if admin_messages:
        for message_id in admin_messages[0].messages_id.split(','):
            chat_id, msg_id = message_id.split()
            try:
                bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception:
                pass
        admin_messages[0].delete()


def get_course(a, b):
    """Получение курса валюты"""
    url = f'https://min-api.cryptocompare.com/data/price?fsym={a}&tsyms={b}'
    response = requests.get(url).json()
    return response[b]


def menu(chat_id):
    """Меню выбора способа обмена"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    change1 = types.InlineKeyboardButton(text='🔀 Обменять в Crypto M кошельке',
                                         callback_data='change|change1_1')
    change2 = types.InlineKeyboardButton(text='💎 Купить или Продать', callback_data='change|change2_1')
    menu = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='menu')
    markup.add(change2, change1, menu)
    bot.send_message(chat_id=chat_id, text='В Сrypto Mystery вы можете Купить криптовалюту на Crytpo M кошелёк, Продать свою криптовалюту со сторонних адресов или прозвести обмен криптовалют на внутреннем кошельке Crypto Mystery', reply_markup=markup)


def change1_1(chat_id, data):
    user = User.objects.get(chat_id=chat_id)
    """Выбор валюты, которую хотят отдать"""
    text = 'Crypto M wallet\n' \
           f'ID: {chat_id}\n' \
           'Баланс вашего кошелька:\n\n' + user.wallet.wallet_balance()
    markup = types.InlineKeyboardMarkup(row_width=4)
    rub = types.InlineKeyboardButton(text='RUB', callback_data=f'change|{data[0]}_2|RUB')
    btc = types.InlineKeyboardButton(text='BTC', callback_data=f'change|{data[0]}_2|BTC')
    eth = types.InlineKeyboardButton(text='ETH', callback_data=f'change|{data[0]}_2|ETH')
    usdt = types.InlineKeyboardButton(text='USDT', callback_data=f'change|{data[0]}_2|USDT')
    trx = types.InlineKeyboardButton(text='TRX', callback_data=f'change|{data[0]}_2|TRX')
    ton = types.InlineKeyboardButton(text='TON', callback_data=f'change|{data[0]}_2|TON')
    xmr = types.InlineKeyboardButton(text='XMR', callback_data=f'change|{data[0]}_2|XMR')
    back = types.InlineKeyboardButton(text='BACK', callback_data=f'change|menu')
    markup.add(rub, btc, eth, usdt, trx, ton, xmr)
    markup.add(back)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def change1_2(chat_id, data):
    """Выбор валюты, которую хотят получить"""
    text = 'Выберите валюту, которую вы хотите получить'
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    if data[0] == 'change2_1_2':
        n = 'change2_1_2_2'
    else:
        n = 'change2_1_2_3'
    if data[0] == 'change1_1_2':
        r = f'change1_1_2_2|{data[1]}'
    elif data[1] in ['RUB', 'USDT']:
        r = f'{n}|{data[1]}|{data[2]}'
    else:
        r = f'{n}|{data[1]}'
    if data[1] != 'RUB':
        buttons.append(types.InlineKeyboardButton(text='RUB', callback_data=f'change|{r}|RUB'))
    if data[1] != 'BTC':
        buttons.append(types.InlineKeyboardButton(text='BTC', callback_data=f'change|{r}|BTC'))
    if data[1] != 'ETH':
        buttons.append(types.InlineKeyboardButton(text='ETH', callback_data=f'change|{r}|ETH'))
    if data[1] != 'USDT':
        buttons.append(types.InlineKeyboardButton(text='USDT', callback_data=f'change|{r}|USDT'))
    if data[1] != 'TRX':
        buttons.append(types.InlineKeyboardButton(text='TRX', callback_data=f'change|{r}|TRX'))
    if data[1] != 'TON':
        buttons.append(types.InlineKeyboardButton(text='TON', callback_data=f'change|{r}|TON'))
    if data[1] != 'XMR':
        buttons.append(types.InlineKeyboardButton(text='XMR', callback_data=f'change|{r}|XMR'))
    back = types.InlineKeyboardButton(text='BACK', callback_data=f'change|{data[0][:-2]}')
    markup.add(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4], buttons[5])
    markup.add(back)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def validate(chat_id, a, data):
    """Валидация введенной суммы"""
    if data[0] != 'change2_1_2_2_3':
        first_cur = data[1]
        second_cur = data[2]
        user = User.objects.get(chat_id=chat_id)
        b = user.wallet.check_balance(first_cur, a)
        if data[-1] == '1':
            course = get_course(first_cur, 'USD')
            val = round(a * course, 2)
            b = user.wallet.check_balance(first_cur, a)
            if not b:
                return 'У вас недостаточно средств на балансе'
            if val < 10:
                return f'Минимальная сумма обмена 10 USDT. Вы ввели {val} USDT. Введите большую сумму.'
        else:
            course = get_course(second_cur, 'USD')
            course1 = get_course(second_cur, first_cur)
            val = round(a * course, 2)
            val1 = round(a * course1, 2)
            if not b:
                return 'У вас недостаточно средств на балансе'
            if val < 10:
                return f'Минимальная сумма обмена 10 USDT. Вы ввели {val} USDT. Введите большую сумму.'
    else:
        first_cur = data[1]
        second_cur = data[-2]
        if data[-1] == '1':
            course = get_course(first_cur, 'USD')
            val = round(a * course, 2)
            if val < 10:
                return f'Минимальная сумма обмена 10 USDT. Вы ввели {val} USDT. Введите большую сумму.'
        else:
            course = get_course(second_cur, 'USD')
            val = round(a * course, 2)
            if val < 10:
                return f'Минимальная сумма обмена 10 USDT. Вы ввели {val} USDT. Введите большую сумму.'
    return False

def get_number(number):
    number_str = str(number).split('.')
    formatted_number = " ".join(number_str[0][i:i + 3] for i in range(0, len(number_str[0]), 3))
    try:
        return formatted_number+f',{number_str[1]}'
    except Exception:
        return formatted_number

def change1_3_input(message, chat_id, data, message_id):
    """Обработка ввода того, сколько валюты хочет получить пользователь"""
    user = User.objects.get(chat_id=chat_id)
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        bot.delete_message(chat_id=chat_id, message_id=message.id)
    except Exception:
        pass
    if message.text == '/create':
        menu(chat_id=chat_id)

    try:
        error = 'Введите число, которое больше 0'
        a = float(message.text.replace(',', '.'))
        error = validate(chat_id, a, data)
        if error != False:
            raise Exception
    except Exception as ex:
        change1_3(chat_id, data, error=error)
    else:
        markup = types.InlineKeyboardMarkup(row_width=2)
        if data[0] == 'change1_1_2_2_3':
            if data[-1] == '1':
                course = get_course(data[1], data[2])
                get = get_number(a * course)
                send = get_number(a)
            else:  # отдаем x//3 получаем х
                course = get_course(data[2], data[1])
                get = get_number(a)
                send = get_number(a * course)
            text = f'Вы отдадите {send} {data[1]} и получите {get} {data[2]}'
            cansel = types.InlineKeyboardButton(text='Отменить', callback_data='change|cansel')
            back = types.InlineKeyboardButton(text='Назад',
                                              callback_data=f'change|change1_1_2_2|{data[1]}|{data[2]}|{data[3]}')
            confirm = types.InlineKeyboardButton(text='Одобрить',
                                                 callback_data=f'change|confirm|{data[1]}|{data[2]}')
            markup.add(confirm, cansel, back)
        else:
            if data[-1] == '1':  # отдаем x получаем х//3
                course = get_course(data[1], data[-2])
                get = get_number(a * course)
                send = get_number(a)
                first = f'Для того, чтобы получить {get} {data[-2]}\n'
            else:  # отдаем x//3 получаем х
                course = get_course(data[-2], data[1])
                get = get_number(a)
                send = get_number(a * course)
                first = f'Для того, чтобы получить {get} {data[-2]}\n'
            if data[1] in ['USDT', "RUB"]:
                text = f'{first}' \
                       f'Отправьте {send} {data[1]} на \n\n' \
                       f'{payment[data[1]][data[2]]}'
                if data[1] == 'RUB':
                    text += f'\n\nПросим обратить внимание на правила работы нашего сервиса:\n' \
                            f'1\. Перевод может быть осуществлен только с личной карты\.\n' \
                            f'2\. После совершения перевода перешлите чек в данный чат\.\n' \
                            f'3\. Совершайте перевод исключительно на указанную сумму для каждых реквизитов из списка ниже\.\n'
            else:
                text = f'{first}' \
                       f'Отправьте {send} {data[1]} на \n\n' \
                       f'{payment[data[1]]}'
            cansel = types.InlineKeyboardButton(text='Отменить', callback_data='change|menu')
            back = types.InlineKeyboardButton(text='Назад',
                                              callback_data=f'change|change2_1_2_2|{data[1]}|{data[2]}|{data[3]}')
            confirm = types.InlineKeyboardButton(text='Отправил',
                                                 callback_data=f'change|approve|{data[1]}|{data[-2]}')
            markup.add(confirm, cansel, back)
        user.get_cripto = decimal.Decimal(get.replace(',', '.').replace(' ', ''))
        user.send_cripto = decimal.Decimal(send.replace(',', '.').replace(' ', ''))
        user.save()
        bot.send_message(chat_id, text=text, reply_markup=markup, parse_mode='MarkdownV2')


def change1_3(chat_id, data, error=False):
    """Просьба пользователя ввести кол-во валюты, которое хочет получить"""
    if error:
        text = error
    elif data[-1] == '2':
        text = f'Введите сколько {data[-2]} вы хотите получить.'
    else:
        text = f'Введите сколько {data[1]} вы хотите отдать.'
    msg = bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.go_to_menu())
    bot.register_next_step_handler(msg, change1_3_input, chat_id, data, msg.id)


def change1_31(chat_id, data):
    """Выбор банка или сети для USDT"""
    text = f'Выберите способ оплаты.'
    markup = types.InlineKeyboardMarkup(row_width=3)
    back = types.InlineKeyboardButton(text='Назад', callback_data=f'change|{data[0][:-2]}|{data[1]}|')
    if data[1] == 'RUB':
        sber = types.InlineKeyboardButton(text='Сбербанк', callback_data=f'change|{data[0]}|{data[1]}|sber')
        #tink = types.InlineKeyboardButton(text='Тинькофф', callback_data=f'change|{data[0]}|{data[1]}|tink')
        gpb = types.InlineKeyboardButton(text='ГПБ', callback_data=f'change|{data[0]}|{data[1]}|gpb')
        psb = types.InlineKeyboardButton(text='ПСБ', callback_data=f'change|{data[0]}|{data[1]}|psb')
        alpha = types.InlineKeyboardButton(text='Альфа Банк', callback_data=f'change|{data[0]}|{data[1]}|alpha')
        markup.add(sber, gpb, psb, alpha)
    else:
        trc20 = types.InlineKeyboardButton(text='TRC20', callback_data=f'change|{data[0]}|{data[1]}|TRC20')
        erc20 = types.InlineKeyboardButton(text='ERC20', callback_data=f'change|{data[0]}|{data[1]}|ERC20')
        bep20 = types.InlineKeyboardButton(text='BEP20', callback_data=f'change|{data[0]}|{data[1]}|BEP20')
        spl = types.InlineKeyboardButton(text='SPL', callback_data=f'change|{data[0]}|{data[1]}|SPL')
        markup.add(trc20, erc20, bep20, spl)
    markup.add(back)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def change2_1_2_2(chat_id, data):
    """Выбор того, что пользователь хочет ввести(Сколько хочет отдать или сколько хочет получить)"""
    user = User.objects.get(chat_id=chat_id)
    text = 'Crypto M wallet\n' \
           f'ID: {chat_id}\n' \
           'Баланс вашего кошелька:\n\n' + user.wallet.wallet_balance()
    markup = types.InlineKeyboardMarkup(row_width=1)
    send_first = f'{data[1]}'
    send_second = f'{data[-1]}'
    if data[1] in ['RUB', 'USDT'] and data[0] != 'change1_1_2_2':
        n = f'change|{data[0][:-2]}|{data[1]}|{data[2]}'
        r = f'change|{data[0]}_3|{data[1]}|{data[2]}|{data[3]}'
    else:
        n = f'change|{data[0][:-2]}|{data[1]}'
        r = f'change|{data[0]}_3|{data[1]}|{data[2]}'
    back = types.InlineKeyboardButton(text='Назад', callback_data=n)
    first = types.InlineKeyboardButton(text=f'Ввести {send_first}', callback_data=f'{r}|1')
    second = types.InlineKeyboardButton(text=f'Ввести {send_second}', callback_data=f'{r}|2')
    markup.add(first, second, back)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


def new_callback(data, user, chat_id):
    """Callback для обработки markup"""
    if data[0] == 'menu':
        menu(chat_id=chat_id)
    elif data[0] in ['change1_1', 'change2_1']:
        change1_1(chat_id=chat_id, data=data)
    elif data[0] in ['change1_1_2', 'change2_1_2']:
        if data[1] in ['RUB', 'USDT'] and len(data) == 2 and data[0] != 'change1_1_2':
            change1_31(chat_id, data)
        else:
            change1_2(chat_id, data)
    elif data[0] in ['change2_1_2_2', 'change1_1_2_2']:
        change2_1_2_2(chat_id, data)
    elif data[0] in ['change1_1_2_2_3', 'change2_1_2_2_3']:
        change1_3(chat_id, data)

    elif data[0] == 'confirm':  # Внутренний перевод
        send_message_to_admin(data=data, chat_id=chat_id)

    elif data[0] == 'approve':  # Внешний перевод
        send_message_to_admin(data=data, chat_id=chat_id)
    elif data[0] == 'adm_approve':
        delite_for_admins(data[-2])
        admin_approve(data=data)
    elif data[0] == 'adm_cansel':
        delite_for_admins(data[-2])
        admin_cansel(data=data)
    else:
        bot.send_message(chat_id=chat_id,
                         text='🧿Crypto Mystery желает вам удачи 🍀 и с нетерпением ждет вашего возвращения!')
