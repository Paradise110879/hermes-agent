import os
import logging
import traceback
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

# تلاش برای بارگذاری و تشخیص ساختار Hermes Agent
agent = None
init_error = None

try:
    # چک کردن ساختارهای مختلف Import در ریپوزیتوری رسمی
    try:
        from hermes_agent.agent import HermesAgent
        agent = HermesAgent()
        print("=== HermesAgent successfully loaded from hermes_agent.agent ===")
    except ImportError:
        try:
            from src.hermes_agent.agent import HermesAgent
            agent = HermesAgent()
            print("=== HermesAgent successfully loaded from src.hermes_agent.agent ===")
        except ImportError:
            import hermes_agent
            print(f"=== Module hermes_agent found. Attributes: {dir(hermes_agent)} ===")
            init_error = f"HermesAgent class not directly found. Available attributes: {dir(hermes_agent)}"
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
            # فراخوانی متد پاسخ‌دهی ایجنت
            if hasattr(agent, 'run'):
                response = agent.run(user_text)
            elif hasattr(agent, 'ask'):
                response = agent.ask(user_text)
            elif hasattr(agent, '__call__'):
                response = agent(user_text)
            else:
                response = f"Agent loaded but no supported call method found. Methods: {dir(agent)}"
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
