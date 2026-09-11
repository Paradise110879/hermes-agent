import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# خروجی لاگ‌ها را آنی و زنده می‌کند
logging.basicConfig(level=logging.INFO)

# فراخوانی ایجنت هرمس (با فرض اینکه هرمس کلاس یا تابع اصلی دارد)
# در صورت نیاز می‌توانید مسیر import را با توجه به ساختار پروژه تغییر دهید
try:
    from hermes_agent import HermesAgent
    agent = HermesAgent()
except Exception as e:
    print(f"Error loading Hermes Agent: {e}")
    agent = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات Hermes Agent روشن و آماده پاسخگویی است.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"Received message: {user_text}")
    
    if agent:
        # ارسال متن به هرمس و دریافت پاسخ
        response = agent.run(user_text) 
    else:
        response = "موتور ایجنت هنوز بارگذاری نشده است."

    await update.message.reply_text(str(response))

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
