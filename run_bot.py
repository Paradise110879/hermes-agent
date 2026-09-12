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

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# آدرس پیش‌فرض 9Router
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://9router.com/v1")
# مدل پیش‌فرض برای کمبو 9Router
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = None
if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_API_BASE
    )

chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_histories[user_id] = [
        {"role": "system", "content": "You are a helpful AI assistant powered by 9Router."}
    ]
    await update.message.reply_text("سلام! ربات متصل به 9Router آماده پاسخ‌دهی است.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if not client:
        await update.message.reply_text("خطا: کلید 9Router در متغیرهای Railway ست نشده است.")
        return

    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant powered by 9Router."}
        ]

    chat_histories[user_id].append({"role": "user", "content": user_text})
    
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-9:]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=chat_histories[user_id]
        )
        
        ai_reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})
        
        await update.message.reply_text(ai_reply)

    except Exception as e:
        error_msg = f"خطا در ارتباط با 9Router:\n{str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg)

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("متغیر TELEGRAM_BOT_TOKEN ست نشده است!")

    print("=== Bot Connected to 9Router Started ===")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
