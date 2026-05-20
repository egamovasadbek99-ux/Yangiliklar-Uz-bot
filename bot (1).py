# bot.py — XabarUZ Telegram Boti (Groq - BEPUL)
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from groq import Groq

# ── SOZLAMALAR ────────────────────────────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "BU_YERGA_BOT_TOKENINGIZNI_QOYING")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY",   "BU_YERGA_GROQ_KALITINGIZNI_QOYING")

logging.basicConfig(level=logging.INFO)
client = Groq(api_key=GROQ_API_KEY)

# ── YANGILIKLAR ───────────────────────────────────────────────
NEWS = [
    {"title": "Prezident O'zbekiston-Xitoy strategik hamkorligini yangi bosqichga ko'tardi", "desc": "5 mlrd dollarlik savdo bitimi imzolandi.", "cat": "siyosat", "emoji": "🏛️"},
    {"title": "O'zbek bokschilar jahon chempionatida 3 ta oltin medal qo'lga kiritdi",       "desc": "Milliy jamoamiz Dubay chempionatida g'olib chiqdi.", "cat": "sport", "emoji": "🥊"},
    {"title": "O'zbekistonda AI strategiyasi 2030 yilgacha tasdiqlandi",                      "desc": "Raqamli texnologiyalar vazirligi yo'l xaritasini e'lon qildi.", "cat": "texnologiya", "emoji": "🤖"},
    {"title": "O'zbekiston eksporti 18 foizga o'sdi",                                        "desc": "Avtomobilsozlik va to'qimachilik yetakchi o'rinda.", "cat": "iqtisod", "emoji": "💹"},
    {"title": "Toshkentda yangi metro liniyasi qurilishi boshlanadi",                         "desc": "Yangi O'zbekiston rayonida metro qurilishi rejalashtirilgan.", "cat": "umumiy", "emoji": "🚇"},
    {"title": "O'zbek kinosi Kan festivaliga tanlandi",                                       "desc": "Yosh rejissyorning filmi yuqori baholandi.", "cat": "madaniyat", "emoji": "🎬"},
    {"title": "Kichik biznesni qo'llab-quvvatlash qonuni qabul qilindi",                     "desc": "3 yil davomida soliqdan ozod etiladi.", "cat": "siyosat", "emoji": "📜"},
    {"title": "U-23 futbol jamoasi Osiyo chempionatiga yo'l oldi",                           "desc": "Yoshlar jamoamiz saralash bosqichini yakunladi.", "cat": "sport", "emoji": "⚽"},
    {"title": "IT Parkda 50 ta startup ishga tushdi, eksport 40% o'sdi",                     "desc": "IT Park rezidentlari soni 350 tadan oshdi.", "cat": "texnologiya", "emoji": "💻"},
    {"title": "O'zbekistonda turizm rekord — 10 million sayyoh",                              "desc": "2025 yilda sayyohlar soni rekord darajaga chiqdi.", "cat": "umumiy", "emoji": "✈️"},
    {"title": "So'm kursi barqarorlik darajasiga erishdi",                                    "desc": "Inflyatsiya 8.5% darajasida nazorat ostida.", "cat": "iqtisod", "emoji": "💰"},
    {"title": "Samarqandda xalqaro musiqa festivali boshlanadi",                              "desc": "30 dan ortiq mamlakat vakillari ishtirok etadi.", "cat": "madaniyat", "emoji": "🎵"},
]

NEWS_TEXT = "\n".join([f'- [{n["cat"]}] {n["title"]}: {n["desc"]}' for n in NEWS])

SYSTEM_PROMPT = f"""Siz "XabarUZ" — O'zbek tilida yangiliklar boti yordamchisisiz.

Mavjud yangiliklar:
{NEWS_TEXT}

Qoidalar:
1. FAQAT O'zbek tilida javob bering
2. Qisqa va aniq javob bering (3-5 gap)
3. Mos yangilik bo'lsa shu haqida gapiring
4. Iliq va professional uslubda, emoji ishlating
5. Telegram uchun *qalin* va _kursiv_ formatting ishlating"""

user_histories = {}

# ── YORDAMCHI FUNKSIYALAR ─────────────────────────────────────
def get_cat_news(cat):
    items = [n for n in NEWS if n["cat"] == cat] if cat != "hammasi" else NEWS
    cat_names = {
        "umumiy": "📋 Umumiy", "siyosat": "🏛️ Siyosat", "iqtisod": "💹 Iqtisod",
        "sport": "⚽ Sport", "texnologiya": "💻 Texnologiya",
        "madaniyat": "🎭 Madaniyat", "hammasi": "📰 Barcha yangiliklar"
    }
    text = f"*{cat_names.get(cat, cat)}:*\n\n"
    for n in items[:5]:
        text += f"{n['emoji']} *{n['title']}*\n_{n['desc']}_\n\n"
    text += "💬 Batafsil bilish uchun savol yozing!"
    return text

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Umumiy",     callback_data="cat_umumiy"),
         InlineKeyboardButton("🏛️ Siyosat",   callback_data="cat_siyosat")],
        [InlineKeyboardButton("💹 Iqtisod",    callback_data="cat_iqtisod"),
         InlineKeyboardButton("⚽ Sport",      callback_data="cat_sport")],
        [InlineKeyboardButton("💻 Texnologiya",callback_data="cat_texnologiya"),
         InlineKeyboardButton("🎭 Madaniyat",  callback_data="cat_madaniyat")],
        [InlineKeyboardButton("📰 Barcha yangiliklar", callback_data="cat_hammasi")],
    ])

# ── BUYRUQLAR ─────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Assalomu alaykum! XabarUZ botiga xush kelibsiz!*\n\n"
        "📰 O'zbekiston va jahon yangiliklari haqida savol bering\n"
        "🗂️ Yoki quyidagi kategoriyalardan birini tanlang:",
        parse_mode="Markdown",
        reply_markup=main_keyboard()
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*📖 Buyruqlar ro'yxati:*\n\n"
        "/start — Bosh menyu\n"
        "/yangiliklar — Barcha yangiliklar\n"
        "/sport — Sport yangiliklari\n"
        "/texnologiya — Texnologiya yangiliklari\n"
        "/iqtisod — Iqtisod yangiliklari\n"
        "/siyosat — Siyosat yangiliklari\n"
        "/tozala — Suhbat tarixini tozalash\n\n"
        "💬 Yoki istalgan savolingizni yozing!",
        parse_mode="Markdown"
    )

async def cmd_yangiliklar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_cat_news("hammasi"), parse_mode="Markdown")

async def cmd_sport(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_cat_news("sport"), parse_mode="Markdown")

async def cmd_texnologiya(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_cat_news("texnologiya"), parse_mode="Markdown")

async def cmd_iqtisod(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_cat_news("iqtisod"), parse_mode="Markdown")

async def cmd_siyosat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_cat_news("siyosat"), parse_mode="Markdown")

async def cmd_tozala(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_histories[update.effective_user.id] = []
    await update.message.reply_text("✅ Suhbat tarixi tozalandi!")

# ── TUGMA BOSILGANDA ──────────────────────────────────────────
async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("cat_"):
        cat = query.data.replace("cat_", "")
        await query.message.reply_text(get_cat_news(cat), parse_mode="Markdown")

# ── AI JAVOB (GROQ) ───────────────────────────────────────────
async def message_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if uid not in user_histories:
        user_histories[uid] = []
    user_histories[uid].append({"role": "user", "content": text})

    # So'nggi 10 xabar saqlanadi
    history = user_histories[uid][-10:]

    await ctx.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Groq'ning bepul kuchli modeli
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *history
            ],
            max_tokens=600,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        user_histories[uid].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Groq API xato: {e}")
        await update.message.reply_text(
            "❌ Xato yuz berdi. Qayta urinib ko'ring yoki /start bosing."
        )

# ── MAIN ──────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start",       start))
    app.add_handler(CommandHandler("help",        help_cmd))
    app.add_handler(CommandHandler("yangiliklar", cmd_yangiliklar))
    app.add_handler(CommandHandler("sport",       cmd_sport))
    app.add_handler(CommandHandler("texnologiya", cmd_texnologiya))
    app.add_handler(CommandHandler("iqtisod",     cmd_iqtisod))
    app.add_handler(CommandHandler("siyosat",     cmd_siyosat))
    app.add_handler(CommandHandler("tozala",      cmd_tozala))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("✅ XabarUZ boti ishga tushdi! (Groq - Bepul)")
    app.run_polling()

if __name__ == "__main__":
    main()
