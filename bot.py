import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import os

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# DATABASE
client = AsyncIOMotorClient(MONGO_URL)
db = client.mafia
users = db.users
games = db.games

# ================= USER =================
async def get_user(user_id):
    user = await users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "coins": 0,  # AnICoIn
            "wins": 0,
            "games": 0
        }
        await users.insert_one(user)
    return user

# ================= START =================
@dp.message(lambda m: m.text == "/start")
async def start(msg: types.Message):
    await get_user(msg.from_user.id)
    await msg.answer("👋 Salom! Mafia botga xush kelibsiz!")

# ================= PROFILE =================
@dp.message(lambda m: m.text == "/me")
async def profile(msg: types.Message):
    user = await get_user(msg.from_user.id)

    text = f"""
⭐ ID: {msg.from_user.id}

👤 {msg.from_user.full_name}

💵 AnICoIn: {user['coins']}

🎯 G‘alaba: {user['wins']}
🎲 Umumiy o‘yinlar: {user['games']}
"""
    await msg.answer(text)

# ================= GAME START =================
@dp.message(lambda m: m.text == "/game")
async def game(msg: types.Message):
    game = await games.find_one({"chat_id": msg.chat.id, "started": False})

    if game:
        return await msg.answer("⚠️ O‘yin allaqachon mavjud!")

    game_data = {
        "chat_id": msg.chat.id,
        "players": [],
        "started": False
    }

    await games.insert_one(game_data)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Join Game", callback_data="join")]
    ])

    await msg.answer("🎲 Mafia o‘yini boshlandi!", reply_markup=kb)

# ================= JOIN =================
@dp.callback_query(lambda c: c.data == "join")
async def join(callback: types.CallbackQuery):
    game = await games.find_one({
        "chat_id": callback.message.chat.id,
        "started": False
    })

    if not game:
        return

    players = game["players"]

    if callback.from_user.id not in players:
        players.append(callback.from_user.id)

        await games.update_one(
            {"_id": game["_id"]},
            {"$set": {"players": players}}
        )

    text = "🎯 O‘yinchilar:\n"
    for i, p in enumerate(players, 1):
        text += f"{i}. <a href='tg://user?id={p}'>Player</a>\n"

    await callback.message.edit_text(text, parse_mode="HTML")

# ================= START GAME =================
@dp.message(lambda m: m.text == "/startgame")
async def start_game(msg: types.Message):
    game = await games.find_one({"chat_id": msg.chat.id, "started": False})

    if not game:
        return await msg.answer("❌ O‘yin topilmadi")

    players = game["players"]

    if len(players) < 3:
        return await msg.answer("❗ Kamida 3 ta o‘yinchi kerak")

    roles = ["mafia", "doctor", "citizen"]
    
    import random
    random.shuffle(players)

    roles_map = {}
    for i, p in enumerate(players):
        role = roles[i % len(roles)]
        roles_map[p] = role

    await games.update_one(
        {"_id": game["_id"]},
        {"$set": {
            "started": True,
            "roles": roles_map
        }}
    )

    # PRIVATE ROLE SEND
    for p in players:
        try:
            await bot.send_message(p, f"🎭 Sizning rolingiz: {roles_map[p]}")
        except:
            pass

    await msg.answer("🎮 O‘yin boshlandi!")

# ================= RUN =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
