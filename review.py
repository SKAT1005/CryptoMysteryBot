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


def send_review_to_admin(user_id, user):
    review = Review.objects.create(author=user, rate=user.rate, value=user.last_value, text=user.text)
    admins = User.objects.filter(is_admin=True)
    admin_message = AdminMessage.objects.create(chat_id=user_id)
    markup = buttons.review_admin(user_id=user_id, review_id=review.id, msg_id=admin_message.id)
    rate = '⭐️' * int(review.rate)
    text = f'Оценка: {rate}\n' \
           f'Сумма операции: {review.value}\n' \
           f'Текст операции: {review.text}'
    messages_id = ''
    bot.send_message(chat_id=user_id, text='🧿👍 - Ваш отзыв будет опубликован в ближайшее время.',
                     reply_markup=buttons.go_to_menu())
    for admin in admins:
        try:
            msg = bot.send_message(chat_id=admin.chat_id, text=text, reply_markup=markup)
            messages_id += f'{admin.id} {msg.id},'
        except Exception as e:
            pass
    admin_message.messages_id = messages_id[:-1]
    admin_message.save()

def delete_for_admins(id):
    """Удаление всех сообщений админам"""
    admin_messages = AdminMessage.objects.get(id=id)
    for message_id in admin_messages.messages_id.split(','):
        chat_id, msg_id = message_id.split()
        try:
            bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
    admin_messages.delete()

def user_approve(user, chat_id):
    rate = '🌟' * user.rate
    text = 'Ваш отзыв:\n' \
           f'Оценка: {rate}\n' \
           f'Текст: {user.text}'
    bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons.user_approve_review())
def review_text(message, chat_id, user, message_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=message.id)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass
    user.text = message.text
    user.save()
    user_approve(user, chat_id=chat_id)



def approve(user_id, review_id, msg_id):
    #delete_for_admins(id=msg_id)
    review = Review.objects.get(id=review_id)
    user = User.objects.get(chat_id=user_id)
    user.wallet.buy('USDT', 1)
    rate = '🌟' * review.rate
    bot.send_message(chat_id=user_id, text='Ваш отзыв одобрен!')
    text = f"➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"👤: *{user.username}*\n\n" \
           f"✅: 💳  ➡️ {review.value}➡️ 🧿\n\n" \
           f"🏆: {rate}\n" \
           "➖➖➖➖➖➖➖➖➖➖➖➖\n" \
           f"{review.text}"
    bot.send_message(chat_id='-1001981218326', text=text.replace('.', '\.'), parse_mode='MarkdownV2')


def callback(data, user, chat_id):
    if data[0] == 'approve':
        approve(user_id=data[1], review_id=data[2], msg_id=data[3])
    elif data[0] == 'rate':
        if len(data) == 1:
            bot.send_message(chat_id=chat_id, text='Выберите оценку, которую хотите поставить нам',
                             reply_markup=buttons.review_rate())
        else:
            bot.send_message(chat_id=chat_id, text='Выберите оценку, которую хотите поставить нам',
                             reply_markup=buttons.review_rate('|edit'))
    elif data[0] == 'text':
        try:
            user.rate = int(data[1])
            user.save()
        except Exception:
            pass
        if len(data) == 3:
            user_approve(user=user, chat_id=chat_id)
        else:
            msg = bot.send_message(chat_id=chat_id, text='Введите текст отзыва')
            bot.register_next_step_handler(msg, review_text, chat_id, user, msg.id)
    elif data[0] == 'send_to_admin':
        send_review_to_admin(chat_id, user)
