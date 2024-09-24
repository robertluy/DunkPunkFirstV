from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

status_or_open_orders = ReplyKeyboardMarkup(resize_keyboard=True)
status_or_open_orders.add('Статусы своих заявок').add('Открытые заявки').add('Выслать решение')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
cancel.add('Отмена')


solver_order_status = InlineKeyboardMarkup(row_width=1)
solver_order_status.add(InlineKeyboardButton(text='Заявки, переданные в работу вам', callback_data='1'),
                        InlineKeyboardMarkup(text='Заявка отменена/выбран другой исполнитель', callback_data='2'),
                        InlineKeyboardMarkup(text='Решение отправлено', callback_data='3'),
                        InlineKeyboardMarkup(text='Вы в рассмотрении студентом', callback_data='4'),
                        InlineKeyboardMarkup(text='Завершено', callback_data='5'))

disciplines = InlineKeyboardMarkup(row_width=1)  # инлайн клавиатура, 2 столбца
disciplines.add(InlineKeyboardButton(text='MATLAB', callback_data='1'),
                InlineKeyboardMarkup(text='Аналитическая геометрия', callback_data='2'),
                InlineKeyboardMarkup(text='Английский язык', callback_data='3'),
                InlineKeyboardMarkup(text='Булевая алгебра', callback_data='4'),
                InlineKeyboardMarkup(text='Архитектура', callback_data='5'),
                InlineKeyboardMarkup(text='Безопасность', callback_data='6'))

order_statuses = InlineKeyboardMarkup(row_width=1)  # инлайн клавиатура, 2 столбца
order_statuses.add(InlineKeyboardButton(text='Выполненные мной:', callback_data='1'),
                   InlineKeyboardMarkup(text='Отказали по заявкам:', callback_data='2'),
                   InlineKeyboardMarkup(text='Я сейчас выполняю', callback_data='3'))

become_solver_or_no = ReplyKeyboardMarkup(resize_keyboard=True)  # ресайз под устройство
become_solver_or_no.add('Да, хочу').add('Отмена')
