# import os
# import sqlite3
# from datetime import datetime, time as dtime
# import pandas as pd
# import pytz
# import asyncio
# import nest_asyncio
# import requests

# from flask import Flask, render_template, request, redirect, url_for
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     CallbackContext,
#     CallbackQueryHandler,
# )

# app = Flask(__name__)
# DB_PATH = 'crm.db'

# BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'
# ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]


# def init_db():
#     if not os.path.exists(DB_PATH):
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#         CREATE TABLE tolovlar (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             ismi TEXT NOT NULL,
#             tolov INTEGER NOT NULL,
#             kurs TEXT NOT NULL,
#             oy TEXT NOT NULL,
#             izoh TEXT,
#             admin TEXT NOT NULL,
#             oqituvchi TEXT NOT NULL,
#             vaqt TEXT NOT NULL,
#             tolov_turi TEXT
#         )
#         ''')
#         con.commit()
#         con.close()

# init_db()

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         ismi = request.form['ismi']
#         tolov = int(request.form['tolov'])
#         if tolov < 1000:
#             tolov *= 1000
#         kurs = request.form['kurs']
#         oy = request.form['oy']
#         izoh = request.form.get('izoh', '')
#         admin = request.form['admin']
#         oqituvchi = request.form['oqituvchi']
#         tolov_turi = request.form['tolov_turi']

#         uzbek_tz = pytz.timezone('Asia/Tashkent')
#         vaqt = datetime.now(uzbek_tz).strftime('%Y-%m-%d %H:%M:%S')

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO tolovlar
#             (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
#         con.commit()
#         con.close()

#         message = (
#             f"\U0001F4B3 *Yangi to‘lov kiritildi!*\n\n"
#             f"\U0001F464 Ismi: {ismi}\n"
#             f"\U0001F4B0 To‘lov: {tolov} so‘m\n"
#             f"\U0001F4DA Kurs: {kurs} ({oy} oyi)\n"
#             f"\U0001F4B3 To‘lov turi: {tolov_turi}\n"
#             f"\U0001F468‍\U0001F3EB O‘qituvchi: {oqituvchi}\n"
#             f"\U0001F9FE Admin: {admin}\n"
#             f"\U0001F4AC Izoh: {izoh or 'Yo‘q'}\n"
#             f"\U0001F552 Sana: {vaqt}"
#         )

#         for admin_id in ADMIN_CHAT_IDS:
#             try:
#                 requests.get(
#                     f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
#                     params={
#                         "chat_id": admin_id,
#                         "text": message,
#                         "parse_mode": "Markdown"
#                     }
#                 )
#             except Exception as e:
#                 print(f"Telegramga xabar yuborishda xatolik: {e}")

#         return redirect(url_for('index'))

#     today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     cur = con.cursor()
#     cur.execute('''
#         SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
#         FROM tolovlar
#         WHERE date(vaqt) = ?
#         ORDER BY vaqt DESC
#     ''', (today,))
#     tolovlar = cur.fetchall()
#     con.close()

#     return render_template('index.html', tolovlar=tolovlar)


# # --- Telegram bot funksiyalari ---
# async def start(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await update.message.reply_text("Siz admin emassiz. Botdan foydalanish uchun ruxsat yo'q.")
#         return

#     oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
#              "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]

#     keyboard = [[InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")]]

#     for oy in oylar:
#         keyboard.append([InlineKeyboardButton(f"🗓 {oy} oyi", callback_data=f"month_{oy.lower()}")])

#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz, admin! Kerakli hisobotni tanlang:", reply_markup=reply_markup)


# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()

#     user_id = query.message.chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await query.edit_message_text("Siz admin emassiz.")
#         return

#     if query.data == "today_report":
#         uzbek_tz = pytz.timezone('Asia/Tashkent')
#         today = datetime.now(uzbek_tz).date().isoformat()

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("""
#             SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
#             FROM tolovlar
#             WHERE DATE(vaqt) = ?
#             ORDER BY vaqt DESC
#         """, (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text("Bugun uchun to‘lovlar yo‘q.")
#             return

#         total_sum = sum(row[1] for row in rows)
#         message = f"\U0001F4C5 *{today}* sanasidagi jami to‘lov: *{total_sum:,}* so‘m"
#         await query.edit_message_text(message, parse_mode="Markdown")

#         os.makedirs("reports", exist_ok=True)
#         df = pd.DataFrame(rows, columns=['ismi', 'tolov', 'kurs', 'oy', 'izoh', 'admin', 'oqituvchi', 'vaqt', 'tolov_turi'])

#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy]
#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"
#             oy_df.to_excel(file_path, index=False)

#             caption = f"\U0001F4C4 {today} - {oy} oyi uchun hisobot"
#             for admin_id in ADMIN_CHAT_IDS:
#                 with open(file_path, 'rb') as f:
#                     await context.bot.send_document(chat_id=admin_id, document=f, caption=caption)

#     elif query.data.startswith("month_"):
#         oy_nomi = query.data.replace("month_", "")

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(f"🗓 {oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#             return

#         total_sum = sum(row[0] for row in rows)
#         await query.edit_message_text(
#             f"🗓 *{oy_nomi.capitalize()}* oyi uchun jami to‘lov: *{total_sum:,}* so‘m",
#             parse_mode="Markdown"
#         )


# async def send_daily_report(context: CallbackContext):
#     uzbek_tz = pytz.timezone('Asia/Tashkent')
#     today_dt = datetime.now(uzbek_tz)
#     today = today_dt.date().isoformat()

#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         for admin_id in ADMIN_CHAT_IDS:
#             await context.bot.send_message(chat_id=admin_id, text="Bugun hech qanday to‘lov bo‘lmadi.")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy]
#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"
#             oy_df.to_excel(file_path, index=False)
#             caption = f"\U0001F4C4 {today_dt.strftime('%d.%m.%Y')} - {oy} oyi uchun hisobot"
#             for admin_id in ADMIN_CHAT_IDS:
#                 await context.bot.send_document(chat_id=admin_id, document=open(file_path, 'rb'), caption=caption)


# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()
#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))
#     app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))
#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()


# if __name__ == '__main__':
#     import threading
#     nest_asyncio.apply()
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()
#     asyncio.run(run_bot())
import os
import sqlite3
from datetime import datetime, time as dtime
import pandas as pd
import pytz
import asyncio
import nest_asyncio
import requests

from flask import Flask, render_template, request, redirect, url_for
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

app = Flask(__name__)
DB_PATH = 'crm.db'

BOT_TOKEN = '7935396412:AAHJS61QJTdHtaf7pNrwtEqNdxZrWgapOR4'
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]

# --- DATABASE ---
def init_db():
    if not os.path.exists(DB_PATH):
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE tolovlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ismi TEXT NOT NULL,
            tolov INTEGER NOT NULL,
            kurs TEXT NOT NULL,
            oy TEXT NOT NULL,
            izoh TEXT,
            admin TEXT NOT NULL,
            oqituvchi TEXT NOT NULL,
            vaqt TEXT NOT NULL,
            tolov_turi TEXT
        )
        ''')
        con.commit()
        con.close()

init_db()

# --- FLASK ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ismi = request.form['ismi']
        tolov = int(request.form['tolov'])
        if tolov < 1000:
            tolov *= 1000
        kurs = request.form['kurs']
        oy = request.form['oy']
        izoh = request.form.get('izoh', '')
        admin = request.form['admin']
        oqituvchi = request.form['oqituvchi']
        tolov_turi = request.form['tolov_turi']
        vaqt = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute('''
            INSERT INTO tolovlar
            (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
        con.commit()
        con.close()

        # Telegramga xabar yuborish
        message = (
            f"💳 *Yangi to‘lov kiritildi!*\n\n"
            f"👤 Ismi: {ismi}\n"
            f"💰 To‘lov: {tolov} so‘m\n"
            f"📚 Kurs: {kurs} ({oy} oyi)\n"
            f"💳 To‘lov turi: {tolov_turi}\n"
            f"👨‍🏫 O‘qituvchi: {oqituvchi}\n"
            f"🛠 Admin: {admin}\n"
            f"💬 Izoh: {izoh or 'Yo‘q'}\n"
            f"🕒 Sana: {vaqt}"
        )

        for admin_id in ADMIN_CHAT_IDS:
            try:
                requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    params={
                        "chat_id": admin_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                )
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")

        return redirect(url_for('index'))

    # Bugungi to‘lovlarni chiqarish
    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute('''
        SELECT ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi
        FROM tolovlar
        WHERE date(vaqt) = ?
        ORDER BY vaqt DESC
    ''', (today,))
    tolovlar = cur.fetchall()
    con.close()

    return render_template('index.html', tolovlar=tolovlar)

# --- TELEGRAM BOT ---
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
        [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat.id

    if user_id not in ADMIN_CHAT_IDS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    # Bugungi to‘lovlar
    if query.data == "today_report":
        today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text("Bugun hech qanday to‘lov yo‘q.")
            return

        total_sum = sum(row[2] for row in rows)
        await query.edit_message_text(f"📅 *{today}* kuni jami to‘lov: *{total_sum:,}* so‘m", parse_mode="Markdown")

        # Hisobot
        df = pd.DataFrame(rows, columns=['id','ismi','tolov','kurs','oy','izoh','admin','oqituvchi','vaqt','tolov_turi'])
        os.makedirs("reports", exist_ok=True)
        for oy in df['oy'].unique():
            oy_df = df[df['oy'] == oy]
            file_path = f"reports/hisobot_{today}_{oy}.xlsx"
            oy_df.to_excel(file_path, index=False)
            for admin_id in ADMIN_CHAT_IDS:
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=admin_id, document=f, caption=f"{oy} oyi - {today}")

    # Oylik menyu
    elif query.data == "oylik_menyu":
        oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
        keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

    # Oylik hisobot
    elif query.data.startswith("month_"):
        oy_nomi = query.data.replace("month_", "")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT tolov FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
            return

        total_sum = sum(row[0] for row in rows)
        await query.edit_message_text(f"🗓 *{oy_nomi.capitalize()}* oyi uchun jami to‘lov: *{total_sum:,}* so‘m", parse_mode="Markdown")

# --- BOTNI ISHGA TUSHIRISH ---
async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))
    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()

# --- KUNLIK HISOBOT (ISTASANGIZ) ---
async def send_daily_report(context: CallbackContext):
    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
    con.close()

    if df.empty:
        for admin_id in ADMIN_CHAT_IDS:
            await context.bot.send_message(chat_id=admin_id, text="Bugun hech qanday to‘lov bo‘lmadi.")
    else:
        os.makedirs("reports", exist_ok=True)
        for oy in df['oy'].unique():
            oy_df = df[df['oy'] == oy]
            file_path = f"reports/hisobot_{today}_{oy}.xlsx"
            oy_df.to_excel(file_path, index=False)
            for admin_id in ADMIN_CHAT_IDS:
                with open(file_path, 'rb') as f:
                    await context.bot.send_document(chat_id=admin_id, document=f, caption=f"{oy} oyi - {today}")

# --- START SERVER & BOT ---
if __name__ == '__main__':
    import threading
    nest_asyncio.apply()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    asyncio.run(run_bot())
