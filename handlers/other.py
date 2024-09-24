from aiogram import types
from creating import dp, bot
import os



async def check_response(message: types.Message):
    tmp = await db.check_user(message.from_user.id)
    if tmp[0] == 1:
        sps = await db.show_presolution_student(message.from_user.id)
        if sps[0][0] != -1:
            for item in sps:
                if item[5] == 0:
                    confirmation_text = f"Ваш заказ N{item[0]}\nИсполнитель N{item[1]}\nДисциплина: {item[2]}\nЦена: {item[3]}\nКомментарий: {item[4]}\n"
                    choose_button = InlineKeyboardMarkup()
                    choose_button.add(InlineKeyboardButton(text="Выбрать",
                                                           callback_data=f"choose_order_{item[1]}choose_order_{item[0]}choose_order_{item[6]}"))
                    await message.answer(confirmation_text, reply_markup=choose_button)
                else:
                    confirmation_text = f"В работе заказ N{item[0]}\nисполнителем N{item[1]}\nДисциплина: {item[2]}\nЦена: {item[3]}\nКомментарий: {item[4]}\n"
                    await message.answer(confirmation_text, reply_markup=kb.cancel)
            await ChatTmp.savage.set()
        else:
            await message.answer('Пусто', reply_markup=kb.cr_or_ch)
    else:
        await message.answer('Для начала определимся кто вы', reply_markup=kb.st_or_sol)


async def process_order_choice(call: types.CallbackQuery, state: FSMContext):
    sp = call.data.split('choose_order_')
    tmp = sp[1]
    ord_id = sp[2]
    pr_id = sp[3]
    await db.check_not_inwork()
    await db.update_presolution_status()
    await call.message.answer(f"Временный чат по заказу N{ord_id} с исполнителем N{tmp} создается...")
    await invite_to_chat(call.from_user.id, int(pr_id), int(ord_id), int(tmp))


async def invite_to_chat(initiator_id: int, target_user_id: int, ord_id: int, id_: int):
    invitation_keyboard = InlineKeyboardMarkup()
    invitation_keyboard.add(InlineKeyboardButton(text="Принять", callback_data=f"accept_chat_{initiator_id}_{ord_id}_{id_}"))
    invitation_keyboard.add(
        InlineKeyboardButton(text="Отклонить", callback_data=f"decline_chat_{initiator_id}_{ord_id}_{id_}"))
    await bot.send_message(
        target_user_id,
        f"{initiator_id} приглашает вас в чат по заказу N{ord_id}. Вы хотите принять?",
        reply_markup=invitation_keyboard
    )


async def process_chat_accept(call: types.CallbackQuery, state: FSMContext):
    sp = call.data.split('_')
    initiator_id = int(sp[2])
    ord_id = sp[3]
    id_ = sp[4]
    await db.update_presolution_status(3, int(ord_id), int(id_))
    target_user_id = call.from_user.id
    active_chats[initiator_id] = target_user_id
    active_chats[target_user_id] = initiator_id
    await bot.send_message(initiator_id,
                           f"Исполнитель N{target_user_id} принял ваше приглашение в чат по заказу N{ord_id}. Можете начать общение.",
                           reply_markup=kb.over)
    await call.message.answer("Вы приняли приглашение. Теперь вы можете общаться в чате.", reply_markup=kb.over)
    initiator_state = dp.current_state(user=initiator_id, chat=initiator_id)
    await initiator_state.finish()
    await state.finish()


async def relay_message(message: types.Message):
    if message.from_user.id in active_chats:
        target_user_id = active_chats[message.from_user.id]
        if message.text == 'Завершить':
            if message.from_user.id in active_chats:
                target_user_id = active_chats[message.from_user.id]
                del active_chats[message.from_user.id]
                del active_chats[target_user_id]
                await bot.send_message(target_user_id, f"{message.from_user.first_name} завершил чат.", reply_markup=kb.st_or_sol)
                await message.answer("Чат завершен.", reply_markup=kb.st_or_sol)
            else:
                await message.answer("Вы не находитесь в активном чате.")
        else:
            await bot.send_message(target_user_id, f"Сообщение от {message.from_user.first_name}: {message.text}",
                                   reply_markup=kb.over)
    else:
        await message.answer("Ошибка: вы не находитесь в активном чате.")


async def end_chat(message: types.Message, state: FSMContext):
    if message.from_user.id in active_chats:
        target_user_id = active_chats[message.from_user.id]
        del active_chats[message.from_user.id]
        del active_chats[target_user_id]
        await bot.send_message(target_user_id, f"{message.from_user.first_name} завершил чат.")
        await message.answer("Чат завершен.")
        target_user_state = dp.current_state(user=target_user_id, chat=target_user_id)
        await target_user_state.finish()
        await state.finish()
    else:
        await message.answer("Вы не находитесь в активном чате.")


async def process_chat_decline(call: types.CallbackQuery, state: FSMContext):
    sp = call.data.split('_')
    initiator_id = int(sp[2])
    ord_id = sp[3]
    current_initiator_state = dp.current_state(user=initiator_id, chat=initiator_id)
    print(f"Текущее состояние инициатора перед завершением: {await current_initiator_state.get_state()}")
    if initiator_id in active_chats:
        del active_chats[initiator_id]
    if call.from_user.id in active_chats:
        del active_chats[call.from_user.id]
    await bot.send_message(initiator_id, f"Исполнитель отклонил ваше приглашение в чат по заказу N{ord_id}.")
    await current_initiator_state.finish()
    print(f"Состояние инициатора после завершения: {await current_initiator_state.get_state()}")
    await state.finish()
    await call.message.answer("Вы отклонили приглашение.")
    await call.answer()
