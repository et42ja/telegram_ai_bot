import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

# ======================
# Logging
# ======================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ======================
# TOKENS from Railway
# ======================
BOT_TOKEN = os.getenv("8428603103:AAGk9W2zJwsid_oLU3as3_ExQjr3AAp20Ec")
OPENAI_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMmIxYzNmZWQtOTBkOS00M2UzLTgyY2MtMDY5YTM3OGRlYTU0IiwidHlwZSI6ImFwaV90b2tlbiJ9.QcMD2v27xCrgzb2jX3eQO28k4G10ucrsWAZXm549Ztw")

if not BOT_TOKEN:
    raise RuntimeError("8428603103:AAGk9W2zJwsid_oLU3as3_ExQjr3AAp20Ec")

if not OPENAI_API_KEY:
    raise RuntimeError("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMmIxYzNmZWQtOTBkOS00M2UzLTgyY2MtMDY5YTM3OGRlYTU0IiwidHlwZSI6ImFwaV90b2tlbiJ9.QcMD2v27xCrgzb2jX3eQO28k4G10ucrsWAZXm549Ztw")

# ======================
# OpenAI Client
# ======================
client = OpenAI(api_key=OPENAI_API_KEY)

# ======================
# Handlers
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 ذكاء اصطناعي", callback_data="ai")],
        [InlineKeyboardButton("🎨 إنشاء صورة", callback_data="image")],
        [InlineKeyboardButton("👨‍💻 معلومات المطور", callback_data="dev")]
    ]
    await update.message.reply_text(
        "🤖 أهلاً بك في بوت الذكاء الاصطناعي\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "ai":
        context.user_data["mode"] = "chat"
        await query.edit_message_text("🧠 أرسل سؤالك")

    elif query.data == "image":
        context.user_data["mode"] = "image"
        await query.edit_message_text("🎨 أرسل وصف الصورة")

    elif query.data == "dev":
        await query.edit_message_text(
            "👨‍💻 المطور: جعفر\n🇮🇶 العراق\n⚙️ Telegram AI Bot"
        )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("mode")

    if mode == "chat":
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": update.message.text}
            ]
        )
        await update.message.reply_text(
            response.choices[0].message.content
        )

    elif mode == "image":
        img = client.images.generate(
            model="gpt-image-1",
            prompt=update.message.text,
            size="1024x1024"
        )
        await update.message.reply_photo(img.data[0].url)

    else:
        await update.message.reply_text("ℹ️ استخدم /start")

# ======================
# Main
# ======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot started successfully")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if name == "main":
    main()

