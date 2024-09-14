from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

st_or_sol = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
st_or_sol.add('Студент').add('Решала')

disciplines = InlineKeyboardMarkup(row_width=1)  # инлайн клавиатура, 2 столбца
disciplines.add(InlineKeyboardButton(text='MATLAB', callback_data='matlab'),
                InlineKeyboardMarkup(text='Аналитическая геометрия', callback_data='analytics_geometry'),
                InlineKeyboardMarkup(text='Английский язык', callback_data='lang_eng'),
                InlineKeyboardMarkup(text='Булевая алгебра', callback_data='boolean algebra'),
                InlineKeyboardMarkup(text='Архитектура', callback_data='architecture'),
                InlineKeyboardMarkup(text='безопасность', callback_data='security'))

confirm = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
confirm.add('Да').add('Нет')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cancel.add('Отмена')

# клавиатуры клиента
