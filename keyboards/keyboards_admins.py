from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('Каталог').add('Корзина').add('Админ-панель')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить товар').add('Удалить товар').add('Взаимодействие с пользователем').add(
    'Сделать рассылку').add('Отмена')

admin_user_exp = ReplyKeyboardMarkup(resize_keyboard=True)
admin_user_exp.add('Корзина по user tg').add('Удалить товар юзера').add('Отмена')

catalog_list = InlineKeyboardMarkup(row_width=2)
catalog_list.add(InlineKeyboardButton(text='Футболки', callback_data='t-shirt'),
                 InlineKeyboardMarkup(text='Кроссовки', callback_data='sneakers'),
                 InlineKeyboardMarkup(text='Другое', callback_data='others'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')

# клавиатуры админа
