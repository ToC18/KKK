# KorpBot/main.py (УПРОЩЕННАЯ РАБОЧАЯ ВЕРСИЯ БЕЗ I18N)

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем роутеры
from commands import router as commands_router
from general import router as general_router
from database.main import init_models

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

load_dotenv()

# --- Получение токена ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("Ошибка: Необходимо установить переменную окружения BOT_TOKEN")
    sys.exit("Ошибка: BOT_TOKEN не найден")

async def main():
    # --- Инициализация ---
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # --- Регистрация роутеров ---
    logger.info("Регистрация роутеров...")
    dp.include_router(commands_router)
    dp.include_router(general_router)
    logger.info("Роутеры зарегистрированы.")

    # --- Инициализация БД ---
    logger.info("Инициализация базы данных...")
    await init_models()
    logger.info("БД инициализирована.")

    # --- Запуск бота ---
    me = await bot.get_me()
    logger.info(f"Бот запущен! ID: {me.id}, Имя: @{me.username}")

    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Запуск получения обновлений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)