from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Апрувнуть решалу').add('Отправить решение (в работе)').add('Обновить статус заявки(в работе)')

# клавиатуры админа
