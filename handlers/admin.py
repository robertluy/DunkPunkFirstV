from aiogram import types, Dispatcher
from creating import dp, bot
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from keyboards import keyboards_admins as kba
from keyboards import keyboards_client as kb
from states import Admin_Approve
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
    if from_name_to_id > 0:
        try:
            await message.answer('Ура, доступ назначен', reply_markup=kba.main_admin)
            async with state.proxy() as data:
                await db.approve_solver_dic(from_name_to_id, int(data['discipline']))
        except:
            await message.answer('что-то пошло не так')
    else:
        await message.answer('что-то пошло не так', reply_markup=kba.main_admin)
    await state.finish()


def register_handler_admin(dp: Dispatcher):
    dp.register_message_handler(cmd_admin_panel, text='Админка')
    dp.register_message_handler(admin_approve, text='Апрувнуть решалу')
    dp.register_callback_query_handler(discipline_chosen_adm, state=Admin_Approve.discipline_list)
    dp.register_message_handler(select_solvers_name, state=Admin_Approve.solver_name)
