from telebot import types

def review_admin(user_id, review_id, msg_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить', callback_data=f'review|approve|{user_id}|{review_id}|{msg_id}')
    cansel = types.InlineKeyboardButton(text='Отказать', callback_data=f'review|cansel|{msg_id}')
    view_user = types.InlineKeyboardButton('Посмотерь аккаунт пользователя', url=f'tg://user?id={user_id}')
    markup.add(approve, cansel, view_user)
    return markup
def review_rate(value):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton(text='⭐️' * i, callback_data=f'review|{value}|{i}'))
    return markup

def review(currensy):
    markup = types.InlineKeyboardMarkup(row_width=1)
    send_review = types.InlineKeyboardButton(text='Оставить отзыв', callback_data=f'review|{currensy}')
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(send_review, menu)
    return markup



def admins_button(id, cripto, user_id, wallet=False):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if wallet:
        user_id = f"{user_id}|{wallet}"
    approve = types.InlineKeyboardButton(text='Одобрить вывод',
                                         callback_data=f'conclusion|approve|{cripto}|{id}|{user_id}')
    cansel = types.InlineKeyboardButton(text='Отменить вывод',
                                        callback_data=f'conclusion|cansel|{cripto}|{id}|{user_id}')
    markup.add(approve, cansel)
    return markup


def conclusion_button(cripto, value, wallet):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить вывод', callback_data=f'conclusion|{cripto}|{value}|{wallet}')
    cansel = types.InlineKeyboardButton(text='Отменить вывод', callback_data=f'menu')
    markup.add(approve, cansel)
    return markup


def send_to_user_button(cripto, user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить перевод', callback_data=f'send_to_user|{cripto}|{user_id}')
    cansel = types.InlineKeyboardButton(text='Отменить перевод', callback_data=f'menu')
    markup.add(approve, cansel)
    return markup


def choose_cripto(param):
    markup = types.InlineKeyboardMarkup(row_width=4)
    rub = types.InlineKeyboardButton(text='RUB', callback_data=f'{param}|RUB')
    btc = types.InlineKeyboardButton(text='BTC', callback_data=f'{param}|BTC')
    eth = types.InlineKeyboardButton(text='ETH', callback_data=f'{param}|ETH')
    usdt = types.InlineKeyboardButton(text='USDT', callback_data=f'{param}|USDT')
    trx = types.InlineKeyboardButton(text='TRX', callback_data=f'{param}|TRX')
    ton = types.InlineKeyboardButton(text='TON', callback_data=f'{param}|TON')
    xmr = types.InlineKeyboardButton(text='XMR', callback_data=f'{param}|XMR')
    back = types.InlineKeyboardButton(text='BACK', callback_data=f'menu')
    markup.add(rub, btc, eth, usdt, trx, ton, xmr)
    markup.add(back)
    return markup


def go_to_menu():
    markup = types.InlineKeyboardMarkup()
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    markup.add(menu)
    return markup


def menu_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    my_wallet = types.InlineKeyboardButton(text='Мой кошелек', callback_data='my_wallet')
    conclusion = types.InlineKeyboardButton(text='Вывести средства', callback_data='conclusion')
    course = types.InlineKeyboardButton(text='Курс криптовалют', callback_data='course')
    change_and_buy = types.InlineKeyboardButton(text='Купить или обменять криптовалюту', callback_data='change|menu')
    history = types.InlineKeyboardButton(text='История операция', callback_data='history')
    markup.add(my_wallet, conclusion, course, history, change_and_buy)
    return markup


def wallet_buttons(chat_id):
    referal_text = 'Приглашаю тебя в бот 🧿 Crypto Mystery!\n\n' \
                   '🧿 Crypto Mystery это:\n\n' \
                   '🔄 Купля/Продажа BTC, ETH, XMR, USDT, TRX, TON\n\n' \
                   'Стать пользователем 🧿 Crypto Mystery можно по ссылке ниже.\n\n' \
                   f'https://t.me/cryptohuibot?start={chat_id}'
    markup = types.InlineKeyboardMarkup(row_width=2)
    conclusion = types.InlineKeyboardButton(text='Вывести средства', callback_data='conclusion')
    change_and_buy = types.InlineKeyboardButton(text='Купить или обменять криптовалюту', callback_data='change|menu')
    menu = types.InlineKeyboardButton(text='Главное меню', callback_data='menu')
    send_to_user = types.InlineKeyboardButton(text='Отправить пользователю бота', callback_data='send_to_user')
    referal = types.InlineKeyboardButton(text='Отправить реферальную ссылку', switch_inline_query=referal_text)
    markup.add(conclusion, change_and_buy, send_to_user, referal, menu)
    return markup
