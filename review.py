import os

import django
import requests

import buttons
import conclusion
import send_to_user
from const import bot
import change_and_buy

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, Wallet, Review, AdminMessage


def send_review_to_admin(user_id, review):
    admins = User.objects.filter(is_admin=True)
    admin_message = AdminMessage.objects.create(chat_id=user_id)
    markup = buttons.review_admin(user_id=user_id, review_id=review.id, msg_id=admin_message.id)
    rate = '⭐️'*int(review.rate)
    text = f'Оценка: {rate}\n' \
           f'Сумма операции: {review.value}\n' \
           f'Текст операции: {review.text}'
    messages_id = ''
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup)
            messages_id += f'{admin.id} {msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()

def delite_for_admins(id):
    """Удаление всех сообщений админам"""
    admin_messages = AdminMessage.objects.get(id=id)
    for message_id in admin_messages.messages_id.split(','):
        chat_id, msg_id = message_id.split()
        try:
            bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
    admin_messages.delete()
def review_text(message, chat_id, user, rate, value, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    value = f'{user.get_cripto} {value}'
    review = Review.objects.create(
        author=user,
        rate=int(rate),
        value=value,
        text=message.text)
    bot.send_message(chat_id=chat_id, text='Спасибо за ваш отзыв. После прохождения модерации вознаграждение будет начислено на ваш кошелек', reply_markup=buttons.go_to_menu())
    send_review_to_admin(chat_id, review)

def approve(user_id, review_id, msg_id):
    delite_for_admins(id=msg_id)
    review = Review.objects.get(id=review_id)
    user = User.objects.get(chat_id=user_id)
    user.wallet.buy('USDT', 1)
    rate = '🌟'*review.rate
    bot.send_message(chat_id=user_id, text='Ваш отзыв одобрен!')
    text = f"Сумма операции: {review.value}\n\n" \
           f"Оценка: {rate}\n" \
           "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"{review.text}"
    bot.send_message(chat_id='-1002120671637', text=text)

def callback(data, user, chat_id):
    if data[0] == 'approve':
        approve(user_id=data[1], review_id=data[2], msg_id=data[3])
    elif len(data) == 1:
        bot.send_message(chat_id=chat_id, text='Выберите оценку, которую хотите поставить нам',
                         reply_markup=buttons.review_rate(value=data[0]))
    elif len(data) == 2:
        msg = bot.send_message(chat_id=chat_id, text='Введите текст отзыва')
        bot.register_next_step_handler(msg, review_text, chat_id, user, data[1], data[0], msg.id)
