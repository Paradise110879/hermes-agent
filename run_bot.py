import sys
import os
import logging
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# خواندن متغیرها از محیط Railway
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# راه‌اندازی کلاینت هوش مصنوعی
client = None
if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )

# تاریخچه کوتاه پیام‌ها برای حفظ حافظه گفتگو
chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_histories[user_id] = [
        {"role": "system", "content": "You are Hermes Agent, a helpful, intelligent AI assistant."}
    ]
    await update.message.reply_text("سلام! من Hermes Agent هستم. چطور می‌توانم کمکتان کنم؟")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if not client:
        await update.message.reply_text("خطا: کلید OPENAI_API_KEY در متغیرهای Railway تنظیم نشده است.")
        return

    # مقداردهی اولیه حافظه کاربر
    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": "You are Hermes Agent, a helpful, intelligent AI assistant."}
        ]

    # افزودن پیام کاربر به تاریخچه
    chat_histories[user_id].append({"role": "user", "content": user_text})
    
    # نگه‌داشتن فقط ۱۰ پیام اخیر برای مدیریت حافظه
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-9:]

    try:
        # ارسال پیام به هوش مصنوعی
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_histories[user_id]
        )
        
        ai_reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})
        
        await update.message.reply_text(ai_reply)

    except Exception as e:
        error_msg = f"خطا در دریافت پاسخ از مدل:\n{str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg)

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("متغیر TELEGRAM_BOT_TOKEN ست نشده است!")

    print("=== Hermes Agent Telegram Bot is Starting ===")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
