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

wallets = [json.loads(i) for i in wallets.strip().splitlines()]
users = [json.loads(i) for i in users.strip().splitlines()]
historys = [json.loads(i) for i in historys.strip().splitlines()]

for i in users:
    print(i)
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
    send_value = i['send_value']
    send_crypto = i['send_crypto']
    get_value = i['get_value']
    get_crypto = i['get_crypto']
    course = i['course']
    adress = i['adress']
    date = datetime.datetime.strptime(i['date'], "%Y-%m-%d-%H:%M:%S")
    user = User.objects.get(chat_id=i['user'])
    History.objects.create(
        user=user,
        type=type,
        send_value=send_value,
        send_crypto=send_crypto,
        get_value=get_value,
        get_crypto=get_crypto,
        course=course,
        adress=adress,
        date=date,
    )
