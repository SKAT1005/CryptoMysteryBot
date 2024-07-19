import datetime
import decimal
import os
import time

import django
import requests
from telebot import types

import analytics
import buttons
import conclusion
import const
import history
import review
import send_to_user
from const import bot
import change_and_buy
import replenishment

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, Wallet


def menu(chat_id):
    text = '👋🧿 - Добро пожаловать. Чем я могу Вам помочь?'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.menu_buttons(chat_id))

@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    entities = []
    text = '🦾 Возможности Крипто-Бота:\n\n🔄 Новый обмен /create\nДанная команда позволяет осуществить:\n- обмен криптовалюты и фиата;\n- мгновенный обмен с выводом на Ваш сторонний кошелёк;\n- пополнение внутреннего электронного кошелька.\n    \n💳 е-Кошелек /e_wallet\nПокажет Ваш внутренний электронный кошелёк с возможностью пополнить или вывести средства. Кошелёк позволяет хранить все перечисленные виды криптовалюты и фиата без комиссий и платежей.\n\n-Пополнение кошелька.\n*При переводе криптовалюты или фиата на адреса или счета бота комиссия 0%.\n-Вывод средств.\n\n🤝 Реферальная программа /referal_url\nПоделитесь возможностью  использовать Крипто-Бот с друзьями и знакомыми.\nПолучайте вознаграждения за активность приглашенных пользователей в виде процента от сделки.\n    \n📝 История сделок /history\nПредоставит Вашу суммарную статистику по каждой монете и общую сумму обмена в usdt.\n    \n❓ В случае возникновения любых вопросов, их можно написать в данный чат (@Crypto_Mystery_Operator).\nНаши операторы помогут Вам. Кроме того, мы всегда открыты для пожеланий по развитию Крипто-Бота.',
    for n in const.entety:
        entities.append(
            types.MessageEntity(type=n['type'], offset=n['offset'], length=n['length'])
        )
    bot.send_message(chat_id, text, entities=entities)


@bot.message_handler(commands=['feedbacks'])
def feedbacks(message):
    chat_id = message.chat.id
    text = '🧿👇 - Здесь вы можете ознакомиться с 💬 отзывами наших клиентов.'
    markup = types.InlineKeyboardMarkup()
    url = types.InlineKeyboardButton('💬Отзывы', url='https://t.me/feedback_crypto_mystery')
    markup.add(url)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

def send_start_message_to_admin(username, chat_id):
    admins = User.objects.filter(is_admin=True)
    markup = types.InlineKeyboardMarkup()
    if username:
        user = types.InlineKeyboardButton(text=username, url=f'tg://user?id={chat_id}')
    else:
        user = types.InlineKeyboardButton(text=chat_id, url=f'tg://user?id={chat_id}')
    markup.add(user)
    for admin in admins:
        if username:
            bot.send_message(chat_id=admin.chat_id, text=f'Произведен старт пользователем @{username}',
                             reply_markup=markup)
        else:
            bot.send_message(chat_id=admin.chat_id, text=f'Произведен старт пользователем id: {chat_id}',
                             reply_markup=markup)

def send_start_message(chat_id):
    text = '👋🧿- Hi!'
    bot.send_message(chat_id=chat_id, text=text)
    text = "🧿 - Подписывайтесь на газету Crypto Mystery📰, где вы сможете узнать об актуальных событиях из мира криптовалют, постоянных конкурсах и новых возможностях данного бота."
    markup = types.InlineKeyboardMarkup()
    url = types.InlineKeyboardButton(text='🇷🇺📰Газета Crypto Mystery', url='https://t.me/+ukhGLz-132JmYWM6')
    markup.add(url)
    bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.first_name
    chat_id = message.chat.id
    if not User.objects.filter(chat_id=chat_id):
        send_start_message_to_admin(username, chat_id)
        send_start_message(chat_id=chat_id)
        wallte = Wallet.objects.create()
        user, _ = User.objects.create(chat_id=chat_id, wallet=wallte, username=username), True
        time.sleep(2)
    else:
        user, _ = User.objects.get(chat_id=chat_id), False
    if _ or not user.referal_id:
        ref_id = message.text.split()
        if len(ref_id) > 1 and User.objects.filter(chat_id=ref_id[1]) and ref_id[1] != str(chat_id):
            user.referal_id = ref_id[1]
            text = 'У вас новый реферал'
            if username:
                text += f': @{username}'
            bot.send_message(chat_id=chat_id)
            user.save()
    menu(chat_id=chat_id)


def wallet(chat_id, user):
    text = f'Crypto M wallet\n' \
           f'ID: `{chat_id}`\n' \
           f'Баланс вашего кошелька:\n\n' + user.wallet.wallet_balance()
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.wallet_buttons(), parse_mode='MarkdownV2')


def get_course(cripto, value='RUB'):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={cripto}&tsyms={value}'
    response = requests.get(url).json()
    return response[value]

def get_sell_course(value):
    n = ''
    url = f'https://min-api.cryptocompare.com/data/price?fsym={value}&tsyms=RUB,BTC,ETH,USDT,TRX,TON,XMR'
    response = requests.get(url).json()
    for i in response:
        cost = format(decimal.Decimal(response[i]).quantize(decimal.Decimal("1.00000000")).normalize(), 'f')
        n += f'{i} -> {value}: {cost}\n'
    return n

def course(chat_id, type, value='RUB'):
    date = datetime.datetime.now()
    msg = bot.send_message(chat_id=chat_id, text='Подождите, пожалуйста. Мы ищем самый актуальный курс')
    text = f'Время обновления: {date.hour}:{date.minute}:{date.second}\n\n'
    if type == 'buy':
        ciptos = ['BTC', 'ETH', 'USDT', 'TRX', 'TON', 'XMR']
        for cripto in ciptos:
            course = get_course(cripto=cripto, value=value)
            text += f'{value} -> {cripto}: {course}\n'
    else:
        text += get_sell_course(value=value)
    bot.edit_message_text(chat_id=chat_id, text=text, message_id=msg.id, reply_markup=buttons.cource(value=value, type=type))


@bot.message_handler(commands=['e_wallet'])
def e_wallet(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    wallet(chat_id=chat_id, user=user)


@bot.message_handler(commands=['create'])
def create(message):
    chat_id = message.chat.id
    change_and_buy.menu(chat_id=chat_id)

@bot.message_handler(commands=['history'])
def histor(message):
    chat_id = message.chat.id
    user = User.objects.get(chat_id=chat_id)
    history.history(user)


@bot.message_handler(commands=['rate'])
def rate(message):
    chat_id = message.chat.id
    course(chat_id=chat_id, type='buy')

@bot.message_handler(commands=['referal_url'])
def referal_url(message):
    chat_id = message.chat.id
    text = '🤝 Реферальная программа:\n\n' \
           'Пригласите партнера в 🧿 Crypto Mystery и получайте от 10% с нашего профита от всех операций реферала!'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.ref(chat_id=chat_id))


@bot.message_handler(content_types='text')
def clear_keyboard(message):
    if message.text in ["🔄 Начать новый обмен", "💳 Ваш Crypto M кошелёк", "🤝 Реферальная программа", "📰 Газета Crypto Mystery", "⚙️ Настройки", "💬 Отзывы",  "❓Справка", "📈 Табло курсов"]:
        chat_id = message.chat.id
        markup = types.ReplyKeyboardRemove()
        bot.send_message(chat_id=chat_id, text='Наш бот обновился, поэтому старая клавиатура у вас удалена. Для взаимодействия с ботом используйте новые кнопки меню или же команды.', reply_markup=markup)
        time.sleep(2)
        menu(chat_id=chat_id)


def commissions(chat_id):
    text = 'Комиссии на вывод:\n\n' \
           f'RUB: 5%\n' \
           f'USDT: 5%\n' \
           f'BTC: 5%\n' \
           f'ETH: 5%\n' \
           f'TRX: 5%\n' \
           f'TON: 5%\n' \
           f'XMR: 5%'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.commissions())


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    message_id = call.message.id
    chat_id = call.message.chat.id
    first_name = call.message.chat.first_name
    msg_text = call.message.text
    user, _ = User.objects.get_or_create(chat_id=call.from_user.id)
    if first_name and first_name != user.username:
        user.username = first_name
        user.save()
    if call.message:
        data = call.data.split('|')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        if data[0] in ['change', 'conclusion', 'replenishment'] and len(data)>=2 and data[1] in ['approve', 'cansel', 'adm_approve', 'adm_cansel']:
            if data[1] in ['approve', 'adm_approve']:
                text = '✅\n' + call.message.text
            else:
                text = '❌\n' + call.message.text
            bot.edit_message_text(chat_id=chat_id, text=text, message_id=message_id)
        else:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except Exception:
                pass
        if data[0] == 'menu':
            user.last_value = ''
            user.text = ''
            user.rate = 1
            user.save()
            menu(chat_id=chat_id)

        elif data[0] == 'change':
            change_and_buy.new_callback(data=data[1:], chat_id=chat_id, user=user, msg_text=msg_text)
        elif data[0] == 'my_wallet':
            wallet(chat_id=chat_id, user=user)
        elif data[0] == 'send_to_user':
            send_to_user.callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'conclusion':
            conclusion.callback(data=data[1:], chat_id=chat_id, user=user, msg_text=msg_text)
        elif data[0] == 'course':
            if len(data) == 3:
                course(chat_id=chat_id, value=data[2], type=data[1])
            else:
                course(chat_id=chat_id, type=data[1])
        elif data[0] == 'review':
            review.callback(data=data[1:], chat_id=chat_id, user=user)
        elif data[0] == 'history':
            history.history(user)
        elif data[0] == 'analytics':
            analytics.analytics(chat_id, user)
        elif data[0] == 'replenishment':
            replenishment.callback(data=data[1:], user=user, chat_id=chat_id, msg_text=msg_text)
        elif data[0] == 'commissions':
            commissions(chat_id)
        else:
            menu(chat_id=chat_id)


bot.infinity_polling(timeout=50, long_polling_timeout=25)
