import sys
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

# اضافه کردن مسیر جاری به PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def get_project_structure(start_path='.'):
    """لیست تمام فایل‌ها و پوشه‌های پایتون پروژه را استخراج می‌کند"""
    tree = []
    ignore_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        rel_path = os.path.relpath(root, start_path)
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            tree.append(f"📁 {rel_path}/\n   📄 " + "\n   📄 ".join(py_files))
    return "\n\n".join(tree) if tree else "هیچ فایل پایتونی یافت نشد."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ربات اسکنر آماده است. یک پیام بفرستید تا ساختار فایل‌ها ارسال شود.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received scan request...")
    structure = get_project_structure()
    response = f"🔍 **ساختار فایل‌های پایتون در پروژه شما:**\n\n{structure}"
    
    # اگر متن خیلی طولانی بود آن را خرد می‌کند
    if len(response) > 4000:
        response = response[:4000] + "\n\n...(ادامه فایل‌ها به دلیل محدودیست تلگرام حذف شد)"
        
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Scanner Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
