import sys
import os
import logging
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://9router.com/v1")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# مدل یا کمبوی اولیه پیش‌فرض
CURRENT_MODEL = os.getenv("MODEL_NAME", "oc/mimo-v2.5-free")

# لیست مدل‌ها یا کمبوهای پیشنهادی شما جهت سوییچ سریع
AVAILABLE_MODELS = [
    "oc/mimo-v2.5-free",
    "oc/muse-spark-1.3-contributor-free",
    "my-combo-name"  # نام کمبویی که در 9Router ساختید را اینجا جایگزین کنید
]

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
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]
    await update.message.reply_text(
        "سلام! من ربات هرمس هستم.\n"
        "برای مشاهده مدل فعال و تغییر آن دستور /model را بزنید."
    )

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش مدل فعال به همراه دکمه‌های تغییر مدل"""
    keyboard = []
    for model in AVAILABLE_MODELS:
        # ساخت دکمه برای هر مدل
        prefix = "✅ " if model == CURRENT_MODEL else ""
        keyboard.append([InlineKeyboardButton(f"{prefix}{model}", callback_data=f"set_model:{model}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg_text = f"🤖 **مدل/کمبوی فعال فعلی:**\n`{CURRENT_MODEL}`\n\nیکی از مدل‌های زیر را برای تغییر انتخاب کنید:"
    await update.message.reply_text(msg_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های تغییر مدل"""
    global CURRENT_MODEL
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("set_model:"):
        selected_model = data.split("set_model:")[1]
        CURRENT_MODEL = selected_model
        
        # بروزرسانی کیبورد جهت نمایش تیک انتخاب
        keyboard = []
        for model in AVAILABLE_MODELS:
            prefix = "✅ " if model == CURRENT_MODEL else ""
            keyboard.append([InlineKeyboardButton(f"{prefix}{model}", callback_data=f"set_model:{model}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ مدل با موفقیت تغییر یافت!\n\n🤖 **مدل فعال فعلی:**\n`{CURRENT_MODEL}`",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    
    if not client:
        await update.message.reply_text("خطا: کلید API ست نشده است.")
        return

    # ارسال وضعیت Typing در تلگرام پیش از فراخوانی API
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    if user_id not in chat_histories:
        chat_histories[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ]

    chat_histories[user_id].append({"role": "user", "content": user_text})
    
    if len(chat_histories[user_id]) > 10:
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-9:]

    try:
        response = client.chat.completions.create(
            model=CURRENT_MODEL,
            messages=chat_histories[user_id]
        )
        
        ai_reply = response.choices[0].message.content
        chat_histories[user_id].append({"role": "assistant", "content": ai_reply})
        
        await update.message.reply_text(ai_reply)

    except Exception as e:
        error_msg = f"خطا در ارتباط با مدل `{CURRENT_MODEL}`:\n{str(e)}"
        print(error_msg)
        await update.message.reply_text(error_msg, parse_mode="Markdown")

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("متغیر TELEGRAM_BOT_TOKEN ست نشده است!")

    print("=== Hermes Telegram Bot Started ===")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("model", model_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
