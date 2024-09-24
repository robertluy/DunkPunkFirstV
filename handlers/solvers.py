from aiogram import types, Dispatcher
from creating import dp, bot
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from states import RegistrationSolver, CheckingOpenOrders, LookAtStatusesSolver
from keyboards import keyboards_solver as kb
from keyboards import keyboards_client as kbc
import DatabaseDP as db
from aiogram.dispatcher.filters import Text
import os


async def choice_solver(message: types.Message):
    el = await db.check_user(message.from_user.id)
    if el[1] and await db.check_any_approve(message.from_user.id):
        await message.answer('Выберите, что хотите посмотреть', reply_markup=kb.status_or_open_orders)
    elif el[1]:
        await message.answer(f"Напишите еще раз {os.getenv('ADMIN_TAG')}")
    else:
        await message.answer(f'Вы в первый раз, давайте знакомиться.\nНомер курса, на котором находитесь?',
                             reply_markup=kb.cancel)
        await RegistrationSolver.course.set()


async def process_course_so(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['course'] = message.text  # Сохраняем курс
    await message.answer('Введите номер вашего телефона (это для админа).')
    await RegistrationSolver.phone.set()


async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text  # Сохраняем курс
    await message.answer('Введите название вашего банка (это для админа).')
    await RegistrationSolver.bank.set()


async def process_bank(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['bank'] = message.text  # Сохраняем курс
    await message.answer('И наконец, название вашего курса (это для студентов).')
    await RegistrationSolver.course_name.set()


async def process_course_name_so(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['course_name'] = message.text  # Сохраняем название курса
    solver_data = {
        'tg_id': message.from_user.id,
        'tg_tag': message.from_user.username,
        'chat_id': message.chat.id,
        'course': data['course'],
        'course_name': data['course_name'],
        'phone': data['phone'],
        'bank': data['bank']
    }
    print(solver_data)
    try:
        await db.add_solver(solver_data)
        await bot.send_message(os.getenv('ADMIN_ID'), f'новый решала {message.from_user.username}')
        await message.answer('Ваш профиль на рассмотрении, напишите @RealRobertL.\nНе меняйте tg_tag до этого момента',
                             reply_markup=kbc.st_or_sol)
    except:
        await message.answer('Что-то пошло не так', reply_markup=kbc.st_or_sol)
    await state.finish()


async def check_open_orders(message: types.Message):
    tmp = await db.check_user(message.from_user.id)
    if tmp[1] == 1:
        await message.answer('Выберите предмет или направленность', reply_markup=kb.disciplines)
        await CheckingOpenOrders.disc.set()
    else:
        pass


async def show_relevant_orders(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(discipline=call.data)
    async with state.proxy() as data:
        orders = await db.show_orders(call.from_user.id, data['discipline'])
    if orders[0] == -1:
        await call.message.answer(f'Пусто',
                                  reply_markup=kb.become_solver_or_no)
        await state.finish()
    else:
        for order in orders:
            document_id = order[5]
            photo_id = order[6]
            order_info = (f"Номер заказа: {order[0]}\n"
                          f"Готово к: {order[1]}\n"
                          f"Создано: {order[2]}\n"
                          f"Комментарий: {order[3]}\n"
                          f"Тип работы: {order[4]}")
            if photo_id:
                await call.message.answer_photo(photo=photo_id)
            if document_id:
                await call.message.answer_document(document=document_id)
            await call.message.answer(order_info)
        await call.message.answer("Выберите номер заказа, который готовы взять", reply_markup=kbc.cancel)
        await CheckingOpenOrders.order.set()


async def choose_ord_id(message: types.Message, state: FSMContext):
    await state.update_data(order=message.text)
    await message.answer('Укажите цену', reply_markup=kbc.cancel)
    await CheckingOpenOrders.price.set()


async def set_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Комментарий для клиента:', reply_markup=kbc.cancel)
    await CheckingOpenOrders.comment.set()


async def write_comment(message: types.Message, state: FSMContext):
    try:
        await state.update_data(comment=message.text)
        async with state.proxy() as data:
            feedback = {
                'sol_id': message.from_user.id,
                'ord_id': data['order'],
                'price': data['price'],
                'comment': data['comment']
            }
        await db.create_presolution(feedback)
        await message.answer('Ваша заявка учтена', reply_markup=kbc.st_or_sol)
    except:
        await message.answer('Произошла какая-то ошибка', reply_markup=kbc.st_or_sol)
    await state.finish()


async def my_orders_statuses_solver(message: types.Message):
    await message.answer('Выберите из списка:', reply_markup=kb.order_statuses)
    await LookAtStatusesSolver.waiting.set()


async def processing_solver(call: types.CallbackQuery, state: FSMContext):
    el = call.data
    await call.message.edit_reply_markup(reply_markup=None)
    if el == '1':
        orders = await db.show_solver_completed(call.from_user.id)
        if orders[0] == -1:
            await call.message.answer(f'Пусто',
                                      reply_markup=kb.status_or_open_orders)
        else:
            for order in orders:
                order_info = (f"Номер заказа: {order[0]}\n"
                              f"Готово к: {order[1]}\n"
                              f"Комментарий: {order[2]}\n"
                              f"Тип работы: {order[3]}")
                await call.message.answer(order_info)
    elif el == '2':
        orders = await db.show_solver_rejected(call.from_user.id)
        if orders[0] == -1:
            await call.message.answer(f'Пусто',
                                      reply_markup=kbc.cancel)
        else:
            for order in orders:
                order_info = (f"Номер заказа: {order[0]}\n"
                              f"Готово к: {order[1]}\n"
                              f"Комментарий: {order[2]}\n"
                              f"Тип работы: {order[3]}")
                await call.message.answer(order_info)
    else:
        orders = await db.show_solver_not_completed(call.from_user.id)
        if orders[0] == -1:
            await call.message.answer(f'Пусто',
                                      reply_markup=kb.status_or_open_orders)
        else:
            for order in orders:
                document_id = order[4]
                photo_id = order[5]
                order_info = (f"Номер заказа: {order[0]}\n"
                              f"Готово к: {order[1]}\n"
                              f"Комментарий: {order[2]}\n"
                              f"Тип работы: {order[3]}")
                if photo_id:
                    await call.message.answer_photo(photo=photo_id)
                if document_id:
                    await call.message.answer_document(document=document_id)
                await call.message.answer(order_info, reply_markup=kb.status_or_open_orders)
    await state.finish()


async def solver_send_solution(message: types.Message):
    await message.answer(f"Свяжитесь с {os.getenv('ADMIN_TAG')}")


def register_handler_solver(dp: Dispatcher):
    dp.register_message_handler(choice_solver, Text(equals='Решала', ignore_case=True))  # Выбор решалы
    dp.register_message_handler(process_course_so, state=RegistrationSolver.course)  # Обработка ввода курса
    dp.register_message_handler(process_phone, state=RegistrationSolver.phone)  # Обработка ввода курса
    dp.register_message_handler(process_bank, state=RegistrationSolver.bank)  # Обработка ввода курса
    dp.register_message_handler(process_course_name_so,
                                state=RegistrationSolver.course_name)  # Обработка названия курса
    dp.register_message_handler(check_open_orders, Text(equals='Открытые заявки', ignore_case=True))
    dp.register_callback_query_handler(show_relevant_orders, state=CheckingOpenOrders.disc)
    dp.register_message_handler(choose_ord_id, state=CheckingOpenOrders.order)
    dp.register_message_handler(set_price, state=CheckingOpenOrders.price)
    dp.register_message_handler(write_comment, state=CheckingOpenOrders.comment)
    dp.register_message_handler(my_orders_statuses_solver, Text(equals='Статусы своих заявок', ignore_case=True))
    dp.register_callback_query_handler(processing_solver, state=LookAtStatusesSolver.waiting)
    dp.register_message_handler(solver_send_solution, Text(equals='Выслать решение', ignore_case=True))

