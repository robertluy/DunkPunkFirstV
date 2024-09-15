from aiogram import executor
import DatabaseDP as db
from creating import dp
from handlers import client, admin


# будет вызвано при запуске бота
async def on_startup(_):
    await db.start_db()  # Вызов функции для инициализации работы с базой данных,
    # тут она создается или проверяется наличие
    print('запуск прошел')


client.register_handler_client(dp)
admin.register_handler_admin(dp)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)  # Запуск бота с использованием long polling
    # игнорирую старые изменения при запуске, экзекьютор - штука ожидающая события от сервера тг, двигатель процесса
# основной файл запуска всего


# все принты нужны для отслеживания местонахождения пользователя в сценарии и проверки формата данных,
# можно не обращать на них внимание
