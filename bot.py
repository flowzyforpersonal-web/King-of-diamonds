import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

Telegram Bot Token

API_TOKEN = '8809659490:AAHnsa2N0Qa54EKlx1Awvduh6M2gKTXstwA'

Logging sozlamalari

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

O'yin holatlarini boshqarish uchun FSM

class GameState(StatesGroup):
waiting_for_number = State()

Har bir chat uchun o'yin seanslarini saqlash

game_sessions = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
await message.answer(
"♦ Alice in Borderland: Olmos Qiroli (King of Diamonds) ♦\n\n"
"O'yin qoidalari:\n"
"1. Ishtirokchilar 0 dan 100 gacha bo'lgan son yuborishadi.\n"
"2. Barcha kiritilgan sonlarning o'rtacha qiymati (Average) hisoblanadi.\n"
"3. O'rtacha qiymat 0.8 ga ko'paytirilib, Nishon son (Target) aniqlanadi.\n"
"4. Nishon songa eng yaqin son kiritgan o'yinchi raundda g'olib bo'ladi!\n\n"
"O'yinni boshlash uchun /oyina buyrug'ini yuboring."
)

@dp.message(Command("oyina"))
async def start_game(message: types.Message, state: FSMContext):
chat_id = message.chat.id
game_sessions[chat_id] = [] # Yangi seans

await state.set_state(GameState.waiting_for_number)
await message.answer(
    "♦ **O'YIN BOSHLANDI!** ♦\n\n"
    "Iltimos, **0 dan 100 gacha** bo'lgan soningizni yuboring.\n"
    "Barcha o'yinchilar son kiritib bo'lgach, /natija buyrug'ini bosing."
)


@dp.message(GameState.waiting_for_number, F.text)
async def process_number(message: types.Message):
# Komandalarni o'tkazib yuborish
if message.text.startswith('/'):
return

try:
    number = float(message.text.replace(',', '.'))
    if not (0 <= number <= 100):
        await message.reply("❌ Iltimos, faqat **0 dan 100 gacha** bo'lgan son kiriting!")
        return
    
    chat_id = message.chat.id
    if chat_id not in game_sessions:
        game_sessions[chat_id] = []
        
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    # Takroriy kiritilganda tanlovni yangilash
    existing_player = next((p for p in game_sessions[chat_id] if p['id'] == user_id), None)
    if existing_player:
        existing_player['choice'] = number
        await message.reply(f"🔄 Tanlovingiz yangilandi: **{number}**")
    else:
        game_sessions[chat_id].append({
            'id': user_id,
            'user': user_name,
            'choice': number
        })
        await message.reply(f"✅ Soningiz qabul qilindi: **{number}**")
    
except ValueError:
    await message.reply("❌ Iltimos, to'g'ri son kiriting (Masalan: 42, 15.5 yoki 80).")


@dp.message(Command("natija"))
async def calculate_results(message: types.Message, state: FSMContext):
chat_id = message.chat.id
players = game_sessions.get(chat_id, [])

if not players:
    await message.answer("⚠️ Hali hech kim son kiritmadi! Avval /oyina ni bosing va son yuboring.")
    return

# Raund hisob-kitoblari
choices = [p['choice'] for p in players]
total_sum = sum(choices)
average = total_sum / len(choices)
target = average * 0.8

# Nishon songa eng yaqin o'yinchini topish
winner = min(players, key=lambda p: abs(p['choice'] - target))

# Natijalarni shakllantirish
result_text = (
    f"📊 **RAUND YAKUNLANDI**\n\n"
    f"👥 Ishtirokchilar: **{len(players)} ta**\n"
    f"📈 O'rtacha qiymat: **{average:.2f}**\n"
    f"🎯 Nishon son (Average × 0.8): **{target:.2f}**\n\n"
    f"🏆 **RAUND G'OLIBI:** {winner['user']} (Tanlagan soni: **{winner['choice']}**)\n\n"
    f"📋 **Barcha tanlovlar:**\n"
)

for p in players:
    diff = abs(p['choice'] - target)
    result_text += f"• {p['user']}: **{p['choice']}** (farq: {diff:.2f})\n"

result_text += "\nYangi raund boshlash uchun /oyina ni bosing."

await message.answer(result_text)

# Seans va FSM ni tozalash
game_sessions[chat_id] = []
await state.clear()


async def main():
print("Bot muvaffaqiyatli ishga tushdi...")
await dp.start_polling(bot)

if name == 'main':
try:
asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
print("Bot to'xtatildi.")