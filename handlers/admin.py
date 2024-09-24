from aiogram import types, Dispatcher
from creating import dp, bot
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from keyboards import keyboards_admins as kba
from keyboards import keyboards_client as kb
from states import Admin_Approve, AdminSendSolution
import DatabaseDP as db
from aiogram.dispatcher.filters import Text
import os


async def delete_message_safe(message: types.Message):
    try:
        await message.delete()
    except:
        pass


async def cmd_admin_panel(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer(f'Вы вошли в админ-панель', reply_markup=kba.main_admin)
    else:
        pass


async def admin_approve(message: types.Message):
    if str(message.from_user.id) == os.getenv('ADMIN_ID'):
        await message.answer(f'Выберите предмет', reply_markup=kb.disciplines)
        await Admin_Approve.discipline_list.set()
    else:
        pass


async def discipline_chosen_adm(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Вы выбрали дисциплину. Укажите tg_tag solver`а, без @", reply_markup=kb.cancel)
    await state.update_data(discipline=call.data)
    await Admin_Approve.solver_name.set()


async def select_solvers_name(message: types.Message, state: FSMContext):
    from_name_to_id = await db.get_solver_id_from_tg_tag(message.text)
    print(from_name_to_id)
    if from_name_to_id > 0:
        try:
            await message.answer('Ура, доступ назначен', reply_markup=kba.main_admin)
            async with state.proxy() as data:
                await db.approve_solver_dic(from_name_to_id, int(data['discipline']))
                await bot.send_message(from_name_to_id,
                                       f"Админ вам назначил доступ на предмет {await db.show_disc_name(int(data['discipline']))}")
        except:
            await message.answer('что-то пошло не так')
    else:
        await message.answer('что-то пошло не так', reply_markup=kba.main_admin)
    await state.finish()


async def send_solution_start(message: types.Message):
    await message.answer('Введите ord_id', reply_markup=kb.cancel)
    await AdminSendSolution.ord.set()


async def send_solution_mid(message: types.Message, state: FSMContext):
    stud = await db.studid_from_ordid(int(message.text))
    await state.update_data(ord_id=int(message.text))
    await state.update_data(student=stud[0])
    if stud[0] == -1:
        await message.answer('Что-то пошло не так', reply_markup=kba.main_admin)
        await state.finish()
    else:
        await message.answer('Приложите ссылку на хранилище', reply_markup=kb.cancel)
        await AdminSendSolution.end.set()


async def send_solution_end(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            pr_id = await db.pr_id_from_order_id(data['ord_id'])
            if pr_id == [-1]:
                raise Exception
            else:
                await db.update_presolution_status(4, int(pr_id[0]))
                await bot.send_message(data['student'], f"Ваше решение по заказу N{data['ord_id']}\n{message.text}",
                                       reply_markup=kb.st_or_sol)
                await message.answer('Отправлено', reply_markup=kba.main_admin)

    except Exception:
        await message.answer('Что-то пошло не так', reply_markup=kba.main_admin)
    await state.finish()


async def start(message: types.Message):
    el = await db.check_user(message.from_user.id)
    if el[0] == 1:
        await message.answer(f'С возвращением, {message.from_user.first_name}', reply_markup=kb.st_or_sol)
    else:
        await message.answer_sticker('CAACAgIAAxkBAAMZZLD7LJq2aaGAHn-OgkVQKDkM9LgAAk0DAAJSOrAFWJ0Eu-ZdkqUvBA')
        await message.answer(f'Здравствуйте, {message.from_user.first_name}. Давайте определимся кто вы',
                             reply_markup=kb.st_or_sol)


async def cmd_cancel(message: types.Message, state: FSMContext):
    cur_st = await state.get_state()
    await message.answer(f'отменяю', reply_markup=kb.st_or_sol)
    if cur_st is None:
        return
    await state.finish()


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_cancel, state='*', commands='Отмена')
    dp.register_message_handler(cmd_cancel, Text(equals='Отмена', ignore_case=True), state='*')
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(cmd_admin_panel, text='Админка')
    dp.register_message_handler(admin_approve, text='Апрувнуть решалу')
    dp.register_callback_query_handler(discipline_chosen_adm, state=Admin_Approve.discipline_list)
    dp.register_message_handler(select_solvers_name, state=Admin_Approve.solver_name)
    dp.register_message_handler(send_solution_start, text='Отправить решение')
    dp.register_message_handler(send_solution_mid, state=AdminSendSolution.ord)
    dp.register_message_handler(send_solution_end, state=AdminSendSolution.end)
