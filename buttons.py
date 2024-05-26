from telebot import types

def review_admin(user_id, review_id, msg_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить', callback_data=f'review|approve|{user_id}|{review_id}|{msg_id}')
    cansel = types.InlineKeyboardButton(text='Отказать', callback_data=f'review|cansel|{msg_id}')
    view_user = types.InlineKeyboardButton('Посмотерь аккаунт пользователя', url=f'tg://user?id={user_id}')
    markup.add(approve, cansel, view_user)
    return markup
def review_rate(n=''):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton(text='⭐️' * i, callback_data=f'review|text|{i}{n}'))
    return markup


def user_approve_review():
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='Одобрить', callback_data='review|send_to_admin')
    edit_rate = types.InlineKeyboardButton(text='Изменить оценку', callback_data='review|rate|edit')
    edit_text = types.InlineKeyboardButton(text='Изменить текст отзыва', callback_data='review|text')
    menu = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='menu')
    markup.add(approve, edit_text, edit_rate, menu)
    return markup

def review():
    markup = types.InlineKeyboardMarkup(row_width=1)
    send_review = types.InlineKeyboardButton(text='Оставить отзыв', callback_data=f'review|rate')
    menu = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='menu')
    markup.add(send_review, menu)
    return markup



def admins_button(id, cripto, user_id, wallet=False):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if wallet:
        user_id = f"{user_id}|{wallet}"
    approve = types.InlineKeyboardButton(text='✅Одобрить вывод',
                                         callback_data=f'conclusion|approve|{cripto}|{id}|{user_id}')
    cansel = types.InlineKeyboardButton(text='❌ Отменить вывод',
                                        callback_data=f'conclusion|cansel|{cripto}|{id}|{user_id}')
    markup.add(approve, cansel)
    return markup


def conclusion_button(cripto, value, wallet):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='✅ Одобрить вывод', callback_data=f'conclusion|{cripto}|{value}|{wallet}')
    cansel = types.InlineKeyboardButton(text='❌ Отменить вывод', callback_data=f'menu')
    markup.add(approve, cansel)
    return markup


def send_to_user_button(cripto, user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    approve = types.InlineKeyboardButton(text='✅ Одобрить перевод', callback_data=f'send_to_user|{cripto}|{user_id}')
    cansel = types.InlineKeyboardButton(text='❌ Отменить перевод', callback_data=f'menu')
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
    menu = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='menu')
    markup.add(menu)
    return markup


def menu_buttons(chat_id):
    referal_text = 'Приглашаю тебя в бот 🧿 Crypto Mystery!\n\n' \
                   '🧿 Crypto Mystery это:\n\n' \
                   '🔄 Купля/Продажа BTC, ETH, XMR, USDT, TRX, TON\n\n' \
                   'Стать пользователем 🧿 Crypto Mystery можно по ссылке ниже.\n\n' \
                   f'https://t.me/cryptohuibot?start={chat_id}'
    markup = types.InlineKeyboardMarkup(row_width=2)
    my_wallet = types.InlineKeyboardButton(text='💳 Ваш кошелек Crypto Mystery', callback_data='my_wallet')
    course = types.InlineKeyboardButton(text='📈 Табло курсов', callback_data='course')
    reviews = types.InlineKeyboardButton(text='💬 Отзывы', url='https://t.me/feedback_crypto_mystery')
    referal = types.InlineKeyboardButton(text='🤝 Отправить реферальную ссылку', switch_inline_query=referal_text)
    newspaper = types.InlineKeyboardButton(text='📰 Газета Crypto Mystery', url='https://t.me/crypto_mystery_news')
    analytics = types.InlineKeyboardButton(text='Аналитика портфеля', callback_data='analytics')
    change_and_buy = types.InlineKeyboardButton(text='🔄 Начать новый обмен', callback_data='change|menu')
    history = types.InlineKeyboardButton(text='История операций', callback_data='history')
    markup.add(change_and_buy)
    markup.add(my_wallet)
    markup.add(referal)
    markup.add(newspaper)
    markup.add(reviews, course)
    markup.add(history, analytics)
    return markup


def wallet_buttons():
    markup = types.InlineKeyboardMarkup(row_width=2)
    conclusion = types.InlineKeyboardButton(text='Вывести 📤', callback_data='conclusion')
    change_and_buy = types.InlineKeyboardButton(text='Пополнить 📥', callback_data='replenishment')
    menu = types.InlineKeyboardButton(text='🏠 Главное меню', callback_data='menu')
    send_to_user = types.InlineKeyboardButton(text='💸 Перевод пользователю Crypto Mystery', callback_data='send_to_user')
    markup.add(change_and_buy, conclusion)
    markup.add(send_to_user)
    markup.add(menu)
    return markup
