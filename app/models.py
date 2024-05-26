from django.db import models


class User(models.Model):
    chat_id = models.CharField(max_length=64, verbose_name='Id чата телеграмма')
    action = models.CharField(max_length=256, default='', blank=True, null=True,
                              verbose_name='Действие пользователя(системное поле)')
    send_cripto = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='Сколько валюты отправляет')
    get_cripto = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='Сколько валюты получает')
    wallet = models.OneToOneField('Wallet', auto_created=True, on_delete=models.CASCADE, verbose_name='Кошелек пользователя')
    referal_id = models.CharField(max_length=32, blank=True, null=True,
                                  verbose_name='ID реферала')
    personal_chat_id = models.CharField(max_length=64, blank=True, null=True, verbose_name='ID персонального чата')
    locale = models.CharField(max_length=32, default='RU', verbose_name='Локализация')
    text = models.TextField(blank=True, null=True,verbose_name='Текст отзыва')
    rate = models.IntegerField(default=1, verbose_name='Оценка отзыва')
    last_value = models.CharField(max_length=256, blank=True, null=True, verbose_name='Значение прошлой сделки')
    is_admin = models.BooleanField(default=False, verbose_name='Является ли пользователь админом')


class Wallet(models.Model):
    rub = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс RUB')
    usdt = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс USDT')
    btc = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс BTC')
    eth = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс ETH')
    trx = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс TRX')
    ton = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс TON')
    xmr = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='баланс XMR')

    def wallet_balance(self):
        return f'RUB: {float(self.rub)}\n' \
               f'USDT: {float(self.usdt)}\n' \
               f'BTC: {float(self.btc)}\n' \
               f'ETH: {float(self.eth)}\n' \
               f'TRX: {float(self.trx)}\n' \
               f'TON: {float(self.ton)}\n' \
               f'XMR: {float(self.xmr)}\n'.replace('.', ',')

    def check_balance(self, cripto, value):
        if getattr(self, cripto.lower()) >= value:
            return True
        return False

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
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='usr', verbose_name='Чья история')
    type = models.CharField(max_length=32, verbose_name='Тип операции')
    send_value = models.DecimalField(default=0, max_digits=1000, decimal_places=8, verbose_name='Сколько валюты отправляет')
    send_cripto = models.CharField(max_length=128, blank=True, verbose_name='Какую криптовалюту отправляете')
    get_value = models.DecimalField(default=0, max_digits=1000, decimal_places=8, blank=True, verbose_name='Сколько валюты получаете')
    get_cripto = models.CharField(max_length=128, blank=True, verbose_name='Какую криптовалюту получаете')
    course = models.FloatField(default=0, verbose_name='Курс операции')
    address = models.CharField(max_length=256, blank=True, verbose_name='Адрес операции')
    date = models.DateField(auto_now_add=True, verbose_name='Дата операции')



