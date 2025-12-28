import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ===== قراءة التوكنات =====
BOT_TOKEN = os.getenv("8428603103:AAGk9W2zJwsid_oLU3as3_ExQjr3AAp20Ec")
OPENAI_API_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMmIxYzNmZWQtOTBkOS00M2UzLTgyY2MtMDY5YTM3OGRlYTU0IiwidHlwZSI6ImFwaV90b2tlbiJ9.QcMD2v27xCrgzb2jX3eQO28k4G10ucrsWAZXm549Ztw")

if not BOT_TOKEN:
    raise ValueError("8428603103:AAGk9W2zJwsid_oLU3as3_ExQjr3AAp20Ec")

# ===== أوامر البوت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔍 بحث", callback_data="search")],
        [InlineKeyboardButton("🎨 إنشاء صورة", callback_data="image")],
        [InlineKeyboardButton("ℹ️ معلومات المطور", callback_data="dev")]
    ]
    await update.message.reply_text(
        "مرحباً بك 👋\nاختر من القائمة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "dev":
        await query.message.reply_text("👨‍💻 المطور: مهندس جعفر")
    elif query.data == "search":
        await query.message.reply_text("✍️ اكتب سؤالك")
    elif query.data == "image":
        await query.message.reply_text("🖼️ أرسل وصف الصورة")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم استلام رسالتك ✅")

# ===== تشغيل البوت =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("✅ Bot is running...")
    app.run_polling(drop_pending_updates=True)

if name == "main":
    main()
