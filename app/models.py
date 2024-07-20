import decimal

import requests
from django.db import models


class User(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id чата телеграмма')
    username = models.CharField(max_length=128, default='Имя отсутствует', verbose_name='Имя пользователя')
    action = models.CharField(max_length=256, default='', blank=True, null=True,
                              verbose_name='Действие пользователя(системное поле)')
    send_cripto = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='Сколько валюты отправляет')
    get_cripto = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='Сколько валюты получает')
    wallet = models.OneToOneField('Wallet', blank=True, on_delete=models.CASCADE, verbose_name='Кошелек пользователя')
    referal_id = models.CharField(max_length=32, blank=True, null=True,
                                  verbose_name='ID реферала')
    personal_chat_id = models.CharField(max_length=64, blank=True, null=True, verbose_name='ID персонального чата')
    locale = models.CharField(max_length=32, default='RU', verbose_name='Локализация')
    text = models.TextField(blank=True, null=True,verbose_name='Текст отзыва')
    rate = models.IntegerField(default=1, verbose_name='Оценка отзыва')
    last_value = models.CharField(max_length=256, blank=True, null=True, verbose_name='Значение прошлой сделки')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')


    def __str__(self):
        return self.chat_id


class Wallet(models.Model):
    rub = models.DecimalField(default=0, max_digits=1000, decimal_places=2, verbose_name='баланс RUB')
    usdt = models.DecimalField(default=0, max_digits=1000, decimal_places=2, verbose_name='баланс USDT')
    btc = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс BTC')
    eth = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс ETH')
    trx = models.DecimalField(default=0, max_digits=1000, decimal_places=5, verbose_name='баланс TRX')
    ton = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс TON')
    xmr = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс XMR')

    def total_balance(self):
        total_usd_balance = self.usdt
        total_RUB_balance = 0
        url = 'https://min-api.cryptocompare.com/data/price?fsym=USDT&tsyms=RUB,BTC,ETH,TRX,TON,XMR'
        responce = requests.get(url).json()
        total_usd_balance += self.rub/ decimal.Decimal(responce['RUB'])
        total_usd_balance += self.btc / decimal.Decimal(responce['BTC'])
        total_usd_balance += self.eth / decimal.Decimal(responce['ETH'])
        total_usd_balance += self.trx / decimal.Decimal(responce['TRX'])
        total_usd_balance += self.ton / decimal.Decimal(responce['TON'])
        total_usd_balance += self.xmr / decimal.Decimal(responce['XMR'])
        total_RUB_balance = total_usd_balance * decimal.Decimal(responce['RUB'])
        return f'Суммарный баланс RUB: {round(float(total_RUB_balance), 2)}\n' \
               f'Суммарный баланс USDT: {round(float(total_usd_balance), 2)}'

    def get_balance(self, cripto):
        if cripto in ['RUB', 'USDT']:
            balance = format(getattr(self, cripto.lower()).quantize(decimal.Decimal("1.00")).normalize(), 'f')
        else:
            balance = format(getattr(self, cripto.lower()).quantize(decimal.Decimal("1.00000000")).normalize(), 'f')
        return balance

    def wallet_balance(self):
        return f'RUB: {float(self.rub)}\n' \
               f'USDT: {float(self.usdt)}\n' \
               f'BTC: {float(self.btc)}\n' \
               f'ETH: {float(self.eth)}\n' \
               f'TRX: {float(self.trx)}\n' \
               f'TON: {float(self.ton)}\n' \
               f'XMR: {float(self.xmr)}\n\n' \
               f'{self.total_balance()}'.replace('.', ',').replace('-', '\-')

    def check_balance(self, cripto, value):
        if getattr(self, cripto.lower()) >= value:
            return True
        return False

    def balance(self, cripto):
        if cripto in ['RUB', 'USDT']:
            balance = format(getattr(self, cripto.lower()).quantize(decimal.Decimal("1.00")).normalize(), 'f')
        else:
            balance = format(getattr(self, cripto.lower()).quantize(decimal.Decimal("1.00000000")).normalize(), 'f')
        return balance

    def change(self, from_cripto, from_value, to_cripto, to_value):
        first_balance = getattr(self, from_cripto.lower())
        second_balance = getattr(self, to_cripto.lower())
        setattr(self, from_cripto.lower(), first_balance - from_value)
        setattr(self, to_cripto.lower(), second_balance + to_value)
        self.save()

    def buy(self, cripto, value):
        balance = getattr(self, cripto.lower())
        setattr(self, cripto.lower(), balance + value)
        self.save()

    def delite_cripto(self, cripto, value):
        balance = getattr(self, cripto.lower())
        setattr(self, cripto.lower(), balance - value)
        self.save()

class AdminMessage(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id чата телеграмма')
    messages_id = models.CharField(max_length=2 ** 13, blank=True, null=True, verbose_name='Номера сообщений админам')

class Review(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE, related_name='author', verbose_name='Автор отзыва')
    rate = models.IntegerField(verbose_name='Оценка')
    value = models.CharField(max_length=128, verbose_name='Сумма транзакции')
    text = models.TextField(verbose_name='Текст отзыва')


class History(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, related_name='usr', verbose_name='Чья история')
    type = models.CharField(max_length=32, null=True, verbose_name='Тип операции')
    send_value = models.DecimalField(default=0, max_digits=1000, null=True, decimal_places=8, verbose_name='Сколько валюты отправляет')
    send_cripto = models.CharField(max_length=128, blank=True, null=True, verbose_name='Какую криптовалюту отправляете')
    get_value = models.DecimalField(default=0, max_digits=1000, decimal_places=8, blank=True, null=True, verbose_name='Сколько валюты получаете')
    get_cripto = models.CharField(max_length=128, blank=True, null=True, verbose_name='Какую криптовалюту получаете')
    course_send = models.FloatField(default=0, null=True, verbose_name='Курс отправленой валюты к USDT')
    course_get = models.FloatField(default=0, null=True, verbose_name='Курс получаемой волюты к USDT')
    address = models.CharField(max_length=256, blank=True, null=True, verbose_name='Адрес операции')
    date = models.DateField(auto_now_add=True, null=True, verbose_name='Дата операции')



