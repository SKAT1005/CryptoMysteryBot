import datetime
import decimal
import json
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from app.models import User, Wallet, History
with open('wallet.json', 'r', encoding='UTF-8') as wallets:
    wallets = wallets.read()
with open('user.json', 'r', encoding='UTF-8') as users:
    users = users.read()
with open('history.json', 'r', encoding='UTF-8') as historys:
    historys = historys.read()

wallets = json.loads(wallets)
users = json.loads(users)
historys = json.loads(historys)

for i in users:
    chat_id = i['chat_id']
    referral_id = i['referral_id']
    wallet_id = i['wallet']
    for f in wallets:
        if int(f['wallet']) == int(wallet_id):
            wallet = Wallet.objects.create(
                    rub=decimal.Decimal(f['rub']),
                    usdt=decimal.Decimal(f['usdt']),
                    btc=decimal.Decimal(f['btc']),
                    eth=decimal.Decimal(f['eth']),
                    trx=decimal.Decimal(f['trx']),
                    ton=decimal.Decimal(f['ton']),
                    xmr=decimal.Decimal(f['xmr']),
                )
            break
    User.objects.create(
            chat_id=chat_id,
            referal_id=referral_id,
            wallet=wallet
        )

for i in historys:
    type = i['type']
    if type == 'Обмен':
        send_value = decimal.Decimal(i['send_value'])
        send_crypto = i['send_crypto']
        get_value = decimal.Decimal(i['get_value'])
        get_crypto = i['get_crypto']
        date = datetime.datetime.strptime(i['date'], "%Y-%m-%d-%H:%M:%S")
        user = User.objects.get(chat_id=i['user'])
        History.objects.create(
            user=user,
            type=type,
            send_value=send_value,
            send_cripto=send_crypto,
            get_value=get_value,
            get_cripto=get_crypto,
            date=date,
        )
    elif type == 'Пополнения':
        send_value = decimal.Decimal(i['send_value'])
        send_crypto = i['send_crypto']
        date = datetime.datetime.strptime(i['date'], "%Y-%m-%d-%H:%M:%S")
        user = User.objects.get(chat_id=i['user'])
        History.objects.create(
            user=user,
            type=type,
            get_value=send_value,
            get_cripto=send_crypto,
            date=date,
        )
    elif type == 'Вывод':
        send_value = decimal.Decimal(i['send_value'])
        send_crypto = i['send_crypto']
        date = datetime.datetime.strptime(i['date'], "%Y-%m-%d-%H:%M:%S")
        user = User.objects.get(chat_id=i['user'])
        History.objects.create(
            user=user,
            type=type,
            send_value=send_value,
            send_cripto=send_crypto,
            address='Информация отсутствует',
            date=date,
        )
    elif type == 'Перевод пользователю':
        send_value = decimal.Decimal(i['send_value'])
        send_crypto = i['send_crypto']
        address = i['adress']
        date = datetime.datetime.strptime(i['date'], "%Y-%m-%d-%H:%M:%S")
        user = User.objects.get(chat_id=i['user'])
        History.objects.create(
            user=user,
            type=type,
            send_value=send_value,
            send_cripto=send_crypto,
            address=address,
            date=date,
        )
