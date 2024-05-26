import os

import django
import httpx as httpx

import buttons
from const import bot
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, History

API_KEY = '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'

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
proxy = "http://sbhoqmie:74kcgxgaf0do@38.154.227.167:5868"
url = "https://api.openai.com/v1/chat/completions"
timeout = httpx.Timeout(timeout=100.0)
proxy_client = httpx.Client(proxies=proxy, timeout=timeout)

def analytics(chat_id, user):
    historys = History.objects.filter(user=user)
    if historys and API_KEY:
        msg = bot.send_message(chat_id=chat_id, text='Подождите минуту, формируем аналитику по вашему портфелю.')
        promt_text = ''
        for history in historys:
            promt_text += f'Тип:{history.type}|' \
                          f'Сумма операции:{history.send_value} {history.send_cripto}|' \
                          f'Что получили: {history.get_value} {history.get_cripto}|' \
                          f'курс операции: {history.course}|' \
                          f'Дата операции: {history.date}\n'
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system",
                 "content": "Ты должен анализировать полученные доходы и расходы, после чего должден сделать короткую справку и советы"},
                {"role": "user", "content": promt_text}
            ]
        }
        response = proxy_client.post(url, headers=headers, json=data)
        print(response.json())
        try:
            text = response.json()['choices'][0]['message']['content']
            bot.edit_message_text(chat_id=chat_id, message_id=msg.id, text=text, reply_markup=buttons.go_to_menu())
        except Exception:
            bot.edit_message_text(chat_id=chat_id, message_id=msg.id, text='Произошла непредвиденная ошибка, повторите попытку чуть позже', reply_markup=buttons.go_to_menu())
    else:
        bot.send_message(chat_id=chat_id, text='У вас еще не было транзакций в нашем боте', reply_markup=buttons.go_to_menu())