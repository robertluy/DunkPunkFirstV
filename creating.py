from aiogram import Bot, Dispatcher
from dotenv import load_dotenv  # по идее надо, чтобы левые люди могли код смотреть, но не получать важные токены
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os  # Для работы с переменными окружения

load_dotenv()  # Загрузка переменных окружения из файла .env
storage = MemoryStorage()  # Создание экземпляра хранилища состояний FSM в памяти
bot = Bot(os.getenv('TOKEN'))  # создание экземпляра бота
dp = Dispatcher(bot=bot, storage=storage)  # экземпляр управленца месседжов и состояний, мозг
# с указанием бота и хранилища состояний


# этот файл в целом нужен только для того, чтобы не возникло конфликта из-за создания здесь экземпляров
# и их экспорта в хендлеры, а хендлеры жкспортируются в Punkyfunky. Если бы этот код был в Punkyfunky,
# возник бы конфликт. То есть нельзя Punkyfunky->handlers->PunkyFunky, но можно creating->handlers->PunkyFunky
