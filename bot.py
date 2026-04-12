import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.game import router as game_router

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

dp.include_router(game_router)

async def main():
    print("Bot ishga tushdi 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
