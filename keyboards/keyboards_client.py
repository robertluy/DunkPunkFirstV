from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

st_or_sol = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
st_or_sol.add('Студент').add('Решала')

cr_or_ch = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cr_or_ch.add('Проверить отклики').add('Создать заявку').add('Отменить заявку')

over = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
over.add('Завершить')

disciplines = InlineKeyboardMarkup(row_width=1)  # инлайн клавиатура, 2 столбца
disciplines.add(InlineKeyboardButton(text='MATLAB', callback_data='1'),
                InlineKeyboardMarkup(text='Аналитическая геометрия', callback_data='2'),
                InlineKeyboardMarkup(text='Английский язык', callback_data='3'),
                InlineKeyboardMarkup(text='Булевая алгебра', callback_data='4'),
                InlineKeyboardMarkup(text='Архитектура', callback_data='5'),
                InlineKeyboardMarkup(text='Безопасность', callback_data='6'))

job_types = InlineKeyboardMarkup(row_width=1)
job_types.add(InlineKeyboardButton(text='Репетиторство', callback_data='1'),
              InlineKeyboardMarkup(text='Домашняя/Лабораторная работа', callback_data='2'))

confirm = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
confirm.add('Да').add('Отмена')


cancel = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cancel.add('Отмена')

# клавиатуры клиента
