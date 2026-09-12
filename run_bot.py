import sys
import os
import logging
import traceback

# اضافه کردن مسیر پروژه به پایتون جهت پیدا کردن سورس‌ها
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

agent = None
init_error = None

# تلاش برای Import ایجنت هرمس
try:
    try:
        from hermes import HermesAgent
        agent = HermesAgent()
        print("=== HermesAgent loaded via 'hermes' ===")
    except ImportError:
        try:
            from hermes_agent import HermesAgent
            agent = HermesAgent()
            print("=== HermesAgent loaded via 'hermes_agent' ===")
        except ImportError:
            from run import main as hermes_main
            print("=== Found run.py in root ===")
except Exception as e:
    init_error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
    print(f"Error initializing Hermes Agent:\n{init_error}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات Hermes Agent فعال است. سوال خود را بپرسید.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"Received message from Telegram: {user_text}")
    
    if agent:
        try:
            if hasattr(agent, 'run'):
                response = agent.run(user_text)
            elif hasattr(agent, 'chat'):
                response = agent.chat(user_text)
            elif hasattr(agent, 'ask'):
                response = agent.ask(user_text)
            else:
                response = f"متد اجرا یافت نشد. المت‌های موجود: {dir(agent)}"
        except Exception as e:
            response = f"خطا در پردازش ایجنت: {str(e)}"
    else:
        response = f"موتور ایجنت بارگذاری نشد.\n\nجزئیات خطا:\n{init_error}"

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
