from aiogram import types, Dispatcher
from creating import dp, bot
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from states import RegistrationStudent, RegistrationSolver, StudentDisciplineChoice
from keyboards import keyboards_client as kb
import DatabaseDP as db
from aiogram.dispatcher.filters import Text
import os

HELP_FILE_PATH_US = "user_help.txt"  # это файл-справка для клиента, такая структура более удобна для редактирования


# Функция для чтения содержимого файла справки юзвера
def read_help_file_us():
    with open(HELP_FILE_PATH_US, "r", encoding="utf-8") as file:
        return file.read()


# функция-вывод справки ролям
async def help_but_cl(message: types.Message):  # принимаю месседж, чтобы понять кому выводить
    help_text_us = read_help_file_us()
    await message.answer('Вы читаете памятку помощи клиенту')
    await message.answer(help_text_us)


# @dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if await db.check_user(message.from_user.id) != [0, 0]:
        await message.answer(f'С возвращением, {message.from_user.first_name}', reply_markup=kb.st_or_sol)
    else:
        await message.answer_sticker('CAACAgIAAxkBAAMZZLD7LJq2aaGAHn-OgkVQKDkM9LgAAk0DAAJSOrAFWJ0Eu-ZdkqUvBA')
        await message.answer(f'Здравствуйте, {message.from_user.first_name}. Давайте определимся кто вы',
                             reply_markup=kb.st_or_sol)


async def choice_student(message: types.Message):
    if await db.check_user(message.from_user.id) != [0, 0]:
        await message.answer('Выберите предмет или направленность', reply_markup=kb.disciplines)
        await StudentDisciplineChoice.discipline_list.set()
    else:
        await message.answer(f'Прежде чем начнем, ответим на пару вопросов', reply_markup=kb.st_or_sol)
        await message.answer(f'На каком вы курсе?', reply_markup=kb.cancel)
        await RegistrationStudent.course.set()


async def process_course(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['course'] = message.text  # Сохраняем курс
    await message.answer('Введите название вашего курса.')
    await RegistrationStudent.next()


async def process_course_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['course_name'] = message.text  # Сохраняем название курса
    student_data = {
        'tg_id': message.from_user.id,
        'chat_id': message.chat.id,
        'course': data['course'],
        'course_name': data['course_name']
    }
    await db.add_student(student_data)
    await message.answer('Вы зарегестрированы, давайте выберем действие', reply_markup=kb.st_or_sol)
    await state.finish()


# Функция для выбора дисциплины
async def discipline_chosen(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Вы выбрали дисциплину. Укажите дату окончания в формате YYYY-MM-DD")
    await state.update_data(discipline=call.data)
    await StudentDisciplineChoice.period.set()


# Функция для ввода периода
async def period_input(message: types.Message, state: FSMContext):
    await message.answer(
        "Укажите дополнительные комментарии или требования к работе. Если нет комментариев, напишите 'Нет'.")
    await state.update_data(period=message.text)
    await StudentDisciplineChoice.comment.set()


# Функция для ввода комментариев
async def comment_input(message: types.Message, state: FSMContext):
    await message.answer("Укажите тип работы (например: контрольная, лабораторная и т.д.).")
    await state.update_data(comment=message.text)
    await StudentDisciplineChoice.job_type.set()


# Функция для ввода типа работы
async def job_type_input(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото или документ, связанный с заданием (если есть), или нажмите 'Пропустить'.")
    await state.update_data(job_type=message.text)
    await StudentDisciplineChoice.photo.set()


# Функция для прикрепления фото/документа
@dp.message_handler(content_types=['photo', 'document'], state=StudentDisciplineChoice.photo)
async def photo_document_input(message: types.Message, state: FSMContext):
    if message.photo:
        file_id = message.photo[-1].file_id
        await state.update_data(photo=file_id)
    elif message.document:
        file_id = message.document.file_id
        await state.update_data(document=file_id)

    # После прикрепления фото или документа, спрашиваем подтверждение
    await message.answer("Вы хотите подтвердить заявку? Да/Нет", reply_markup=kb.confirm)
    await StudentDisciplineChoice.next()


async def finalize_order(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        # Сохраняем введенные данные в базу
        order_data = {
            'period': data['period'],
            'comment': data['comment'],
            'stud_id': data['stud_id'],  # Это ID студента
            'job_id': data['job_id'],  # Тип работы
            'disc_id': data['disc_id']  # Дисциплина
        }
        order_id = await db.add_order(order_data)

        # Если есть фото или документы, прикрепляем их к заявке
        if 'photo' in data:
            photo_data = {'ord_id': order_id, 'photo': data['photo']}
            await db.add_photo(photo_data)
        if 'doc' in data:
            doc_data = {'ord_id': order_id, 'doc': data['doc']}
            await db.add_document(doc_data)

        # Собираем данные для отправки студенту на подтверждение
        confirmation_text = f"Период выполнения: {data['period']}\nКомментарий: {data['comment']}\nДисциплина: {data['disc_name']}\nТип работы: {data['job_name']}"

        await message.answer(confirmation_text)
        # Отправляем фото, если оно есть
        if 'photo' in data:
            photo_file = InputFile(data['photo'])
            await message.answer_photo(photo=photo_file)

        # Отправляем документ, если он есть
        if 'doc' in data:
            doc_file = InputFile(data['doc'])
            await message.answer_document(document=doc_file)

        # Спрашиваем подтверждение
        await message.answer("Подтверждаете заявку? (Да/Нет)", reply_markup=kb.confirm)

        # Переходим в состояние ожидания подтверждения
        await StudentDisciplineChoice.next()


async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        async with state.proxy() as data:
            order_id = data['order_id']
        # Обновляем статус заявки на 1 (подтверждено)
        await db.update_order_status(order_id, 1)
        await message.answer("Заявка подтверждена.")
    else:
        await message.answer("Заявка не подтверждена.")
    await state.finish()


async def cmd_cancel(message: types.Message, state: FSMContext):
    cur_st = await state.get_state()
    await message.answer(f'отменяю', reply_markup=kb.st_or_sol)
    if cur_st is None:
        return
    await state.finish()


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, state='*', commands='Отмена')
    dp.register_message_handler(cmd_cancel, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(start, commands=['start'])

    dp.register_message_handler(choice_student, Text(equals='Студент', ignore_case=True))  # Выбор студента
    dp.register_message_handler(process_course, state=RegistrationStudent.course)  # Обработка ввода курса
    dp.register_message_handler(process_course_name, state=RegistrationStudent.course_name)  # Обработка названия курса
    dp.register_callback_query_handler(discipline_chosen,
                                       state=StudentDisciplineChoice.discipline_list)  # Обработка выбора дисциплины
    dp.register_message_handler(period_input, state=StudentDisciplineChoice.period)  # Обработка ввода периода
    dp.register_message_handler(comment_input, state=StudentDisciplineChoice.comment)  # Обработка комментариев
    dp.register_message_handler(job_type_input, state=StudentDisciplineChoice.job_type)  # Обработка типа работы
    dp.register_message_handler(finalize_order, state=StudentDisciplineChoice.finalize)  # после комментария финализируем
    dp.register_message_handler(process_confirmation, state=StudentDisciplineChoice.confirmation)  # обработка подтверждения