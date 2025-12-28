import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from openai import OpenAI

# ------------------ تحميل المتغيرات ------------------
load_dotenv()

BOT_TOKEN = os.getenv("8428603103:AAGk9W2zJwsid_oLU3as3_ExQjr3AAp20Ec")
OPENAI_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMmIxYzNmZWQtOTBkOS00M2UzLTgyY2MtMDY5YTM3OGRlYTU0IiwidHlwZSI6ImFwaV90b2tlbiJ9.QcMD2v27xCrgzb2jX3eQO28k4G10ucrsWAZXm549Ztw")

client = OpenAI(api_key=OPENAI_KEY)

# ------------------ تخزين البيانات ------------------
user_history = {}      # البحث السابق لكل مستخدم
waiting_for_image = set()  # المستخدمين الذين طلبوا تعديل صور

# ------------------ /start ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 البحث السابق", callback_data="history")],
        [InlineKeyboardButton("🎨 إنشاء / تعديل صور", callback_data="image")],
        [InlineKeyboardButton("👨‍💻 معلومات المطور", callback_data="dev")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "أهلاً بك 👋\nاختر من القائمة:",
        reply_markup=reply_markup
    )

# ------------------ التعامل مع الأزرار ------------------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "history":
        history = user_history.get(query.from_user.id, [])
        text = "\n".join(history[-5:]) if history else "لا يوجد بحث سابق."
        await query.message.reply_text(f"📜 البحث السابق:\n{text}")

    elif query.data == "dev":
        await query.message.reply_text(
            "👨‍💻 مطور البوت:\n"
            "الاسم: جعفر\n"
            "بوت ذكاء اصطناعي متقدم\n"
            "📧 Telegram Bot Developer"
        )

    elif query.data == "image":
        waiting_for_image.add(query.from_user.id)
        await query.message.reply_text(
            "🎨 أرسل الصورة الآن وسيتم تحليلها أو تعديلها بالذكاء الاصطناعي"
        )

# ------------------ التعامل مع النصوص ------------------
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    # حفظ البحث السابق
    user_history.setdefault(uid, []).append(text)

    # الرد من OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": text}]
    )

    await update.message.reply_text(response.choices[0].message.content)

# ------------------ التعامل مع الصور ------------------
async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in waiting_for_image:
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_url = file.file_path

    waiting_for_image.remove(uid)

    # إرسال الصورة إلى OpenAI لتحليلها
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "حلل هذه الصورة واذكر ما يمكن تحسينه"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
    )

    await update.message.reply_text(
        "🖼️ تحليل الصورة:\n" + response.choices[0].message.content
    )

# ------------------ تشغيل البوت ------------------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
app.add_handler(MessageHandler(filters.PHOTO, image_handler))

app.run_polling()