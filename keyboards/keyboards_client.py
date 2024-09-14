from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

st_or_sol = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
st_or_sol.add('Студент').add('Решала')

disciplines = InlineKeyboardMarkup(row_width=1)  # инлайн клавиатура, 2 столбца
disciplines.add(InlineKeyboardButton(text='MATLAB', callback_data='1'),
                InlineKeyboardMarkup(text='Аналитическая геометрия', callback_data='2'),
                InlineKeyboardMarkup(text='Английский язык', callback_data='3'),
                InlineKeyboardMarkup(text='Булевая алгебра', callback_data='4'),
                InlineKeyboardMarkup(text='Архитектура', callback_data='5'),
                InlineKeyboardMarkup(text='Безопасность', callback_data='6'))

confirm = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
confirm.add('Да').add('Нет')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cancel.add('Отмена')

# клавиатуры клиента
