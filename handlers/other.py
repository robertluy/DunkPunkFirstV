from aiogram import types
from creating import dp, bot
import os


# @dp.message_handler(content_types=['sticker'])
async def check_sticker(message: types.Message):
    await message.answer(message.sticker.file_id)


# @dp.message_handler(content_types=['photo', 'document'])
async def forward_message(message: types.Message):
    await bot.forward_message(os.getenv('GROUP_ID'), message.from_user.id, message.message_id)
    await message.answer('ожидайте')
