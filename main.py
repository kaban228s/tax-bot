import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from app.handlers import main_router, test_router, payment_router

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    dp.include_router(main_router)
    dp.include_router(test_router)
    dp.include_router(payment_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')