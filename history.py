import os

import django
import openpyxl
import buttons

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CryptoMysteryBot.settings')
django.setup()

from const import bot
from app.models import History, User

change_header = ['Дата', 'Вы отдали (валюта)', 'Вы отдали (количество)', 'Вы получили (валюта)', 'Вы получили (количество)', 'Пара обмена', 'Курс обмена']
buy_header = ['Дата', 'Валюта пополнения', 'Способ пополнения', 'Количество', 'Курс']
conclusion_header = ['Дата', 'Валюта вывода', 'Адрес вывода', 'Количество']
send_to_user_header = ['Дата', 'Валюта перевода', 'Количество', 'Кошелен, на который совершен перевод']


def history(user):
    wb = openpyxl.Workbook()
    change_history = History.objects.filter(user=user, type='Обмен')
    buy_history = History.objects.filter(user=user, type='Пополнение')
    conclusion_history = History.objects.filter(user=user, type='Вывод')
    send_to_user_history = History.objects.filter(user=user, type='Перевод пользователю')
    change = wb.create_sheet(title='Обмены')
    buy = wb.create_sheet(title='Пополнения')
    conclusion = wb.create_sheet(title='Выводы')
    send_to_user = wb.create_sheet(title='Переводы пользователям')
    for col, header in enumerate(change_header, start=1):
        change.cell(row=1, column=col, value=header)

    for col, header in enumerate(buy_header, start=1):
        buy.cell(row=1, column=col, value=header)

    for col, header in enumerate(conclusion_header, start=1):
        conclusion.cell(row=1, column=col, value=header)

    for col, header in enumerate(send_to_user_header, start=1):
        send_to_user.cell(row=1, column=col, value=header)

    for row, data in enumerate(change_history, start=2):
        change.cell(row=row, column=1, value=data.date)
        change.cell(row=row, column=2, value=data.send_cripto)
        change.cell(row=row, column=3, value=str(data.send_value))
        change.cell(row=row, column=4, value=data.get_cripto)
        change.cell(row=row, column=5, value=str(data.get_value))
        change.cell(row=row, column=6, value=f'{data.send_cripto} -> {data.get_cripto}')
        change.cell(row=row, column=7, value=data.course)

    for row, data in enumerate(buy_history, start=2):
        buy.cell(row=row, column=1, value=data.date)
        buy.cell(row=row, column=2, value=data.get_cripto)
        buy.cell(row=row, column=3, value=data.send_cripto)
        buy.cell(row=row, column=4, value=str(data.get_value))
        buy.cell(row=row, column=5, value=data.course)

    for row, data in enumerate(conclusion_history, start=2):
        conclusion.cell(row=row, column=1, value=data.date)
        conclusion.cell(row=row, column=2, value=data.send_cripto)
        conclusion.cell(row=row, column=3, value=data.address)
        conclusion.cell(row=row, column=4, value=str(data.send_value))

    for row, data in enumerate(send_to_user_history, start=2):
        send_to_user.cell(row=row, column=1, value=data.date)
        send_to_user.cell(row=row, column=2, value=data.send_cripto)
        send_to_user.cell(row=row, column=3, value=str(data.send_value))
        send_to_user.cell(row=row, column=4, value=data.address)
    wb.save("История операций.xlsx")
    with open('История операций.xlsx', 'rb') as file:
        bot.send_document(chat_id=user.chat_id, document=file, caption='Файл для скачивания',
                          reply_markup=buttons.go_to_menu())