import sys
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def get_project_structure(start_path='.'):
    tree = []
    ignore_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules'}
    for root, dirs, files in os.walk(start_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        rel_path = os.path.relpath(root, start_path)
        py_files = [f for f in files if f.endswith('.py')]
        if py_files:
            tree.append(f"FOLDER: {rel_path}\n   - " + "\n   - ".join(py_files))
    return "\n\n".join(tree) if tree else "No python files found."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ready. Send any message to scan structure.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received scan request...")
    structure = get_project_structure()
    header = "PROJECT STRUCTURE:\n\n"
    full_text = header + structure
    
    # ارسال در قالب تکه‌های امن ۲۰۰۰ تایی بدون Markdown
    chunk_size = 2000
    for i in range(0, len(full_text), chunk_size):
        await update.message.reply_text(full_text[i:i+chunk_size])

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set!")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Scanner Bot is running...")
    # drop_pending_updates=True کانفلیکت‌های قبلی را پاک می‌کند
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
