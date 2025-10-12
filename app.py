
# import os
# import sqlite3
# from datetime import datetime
# import pandas as pd
# import pytz
# import asyncio
# import nest_asyncio
# import requests
# from flask import Flask, render_template, request, redirect, url_for, send_file
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
#             CREATE TABLE tolovlar (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 ismi TEXT NOT NULL,
#                 tolov INTEGER NOT NULL,
#                 kurs TEXT NOT NULL,
#                 oy TEXT NOT NULL,
#                 izoh TEXT,
#                 admin TEXT NOT NULL,
#                 oqituvchi TEXT NOT NULL,
#                 vaqt TEXT NOT NULL,
#                 tolov_turi TEXT
#             )
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
#         vaqt = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d %H:%M:%S')

#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute('''
#             INSERT INTO tolovlar (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
#         con.commit()
#         con.close()

#         message = (
#             f"💳 *Yangi to‘lov kiritildi!*\n\n"
#             f"👤 Ismi: {ismi}\n"
#             f"💰 To‘lov: {tolov:,} so‘m\n"
#             f"📚 Kurs: {kurs} ({oy} oyi)\n"
#             f"💳 To‘lov turi: {tolov_turi}\n"
#             f"👨‍🏫 O‘qituvchi: {oqituvchi}\n"
#             f"🛠 Admin: {admin}\n"
#             f"💬 Izoh: {izoh or 'Yo‘q'}\n"
#             f"🕒 Sana: {vaqt}"
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
#                 print(f"Xabar yuborishda xatolik: {e}")

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


# @app.route('/download_excel')
# def download_excel():
#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar ORDER BY vaqt DESC", con)
#     con.close()
#     if df.empty:
#         return "Bazadan ma'lumot topilmadi."
#     file_path = "tolovlar.xlsx"
#     df.to_excel(file_path, index=False)
#     return send_file(file_path, as_attachment=True)


# # ---------- TELEGRAM BOT QISMI ----------

# async def start(update: Update, context: CallbackContext):
#     user_id = update.effective_chat.id
#     if user_id not in ADMIN_CHAT_IDS:
#         await update.message.reply_text("Siz admin emassiz.")
#         return

#     keyboard = [
#         [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
#         [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=reply_markup)


# async def handle_callback(update: Update, context: CallbackContext):
#     query = update.callback_query
#     await query.answer()
#     user_id = query.message.chat.id

#     if user_id not in ADMIN_CHAT_IDS:
#         await query.edit_message_text("Siz admin emassiz.")
#         return

#     if query.data == "today_report":
#         today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov_turi, SUM(tolov) FROM tolovlar WHERE DATE(vaqt) = ? GROUP BY tolov_turi", (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(
#                 f"📅 *{today}* kuni hech qanday to‘lov yo‘q.",
#                 parse_mode="Markdown"
#             )
#             return

#         naqd = sum(row[1] for row in rows if row[0].lower() == "naqd")
#         karta = sum(row[1] for row in rows if row[0].lower() == "click" or row[0].lower() == "karta")
#         jami = naqd + karta

#         await query.edit_message_text(
#             f"🗓 *{today}* uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd:,} so‘m\n"
#             f"💳 Karta: {karta:,} so‘m\n"
#             f"📊 Jami: {jami:,} so‘m",
#             parse_mode="Markdown"
#         )

#     elif query.data == "oylik_menyu":
#         oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
#                  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
#         keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

#     elif query.data.startswith("month_"):
#         oy_nomi = query.data.replace("month_", "")
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov_turi, SUM(tolov) FROM tolovlar WHERE lower(oy) = lower(?) GROUP BY tolov_turi", (oy_nomi,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(f"🗓 {oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#             return

#         naqd = sum(row[1] for row in rows if row[0].lower() == "naqd")
#         karta = sum(row[1] for row in rows if row[0].lower() in ["click", "karta"])
#         jami = naqd + karta

#         await query.edit_message_text(
#             f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd:,} so‘m\n"
#             f"💳 Karta: {karta:,} so‘m\n"
#             f"📊 Jami: {jami:,} so‘m",
#             parse_mode="Markdown"
#         )


# async def run_bot():
#     app_bot = Application.builder().token(BOT_TOKEN).build()
#     app_bot.add_handler(CommandHandler("start", start))
#     app_bot.add_handler(CallbackQueryHandler(handle_callback))
#     print("✅ Bot ishga tushdi.")
#     await app_bot.run_polling()


# if __name__ == '__main__':
#     import threading
#     nest_asyncio.apply()
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
#     asyncio.run(run_bot())

import os
import sqlite3
from datetime import datetime, time, timedelta
import pandas as pd
import pytz
import asyncio
import nest_asyncio
import threading
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file
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
            INSERT INTO tolovlar (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ismi, tolov, kurs, oy, izoh, admin, oqituvchi, vaqt, tolov_turi))
        con.commit()
        con.close()

        message = (
            f"💳 *Yangi to‘lov kiritildi!*\n\n"
            f"👤 Ismi: {ismi}\n"
            f"💰 To‘lov: {tolov:,} so‘m\n"
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
                    params={"chat_id": admin_id, "text": message, "parse_mode": "Markdown"}
                )
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")

        return redirect(url_for('index'))

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


def create_excel(filter_query, params, fayl_nomi):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(filter_query, con, params=params)
    con.close()

    if df.empty:
        print("Ma'lumot topilmadi.")
        return None

    karta = df[df['tolov_turi'].str.lower().isin(['karta', 'click'])]['tolov'].sum()
    naqd = df[df['tolov_turi'].str.lower() == 'naqd']['tolov'].sum()
    jami = karta + naqd

    df.to_excel(fayl_nomi, index=False)

    with pd.ExcelWriter(fayl_nomi, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        summary = pd.DataFrame({
            'Ismi': ['💵 Jami to‘lovlar:'],
            'tolov': [f"{jami:,} so‘m"],
            'kurs': ['💳 Karta:'],
            'oy': [f"{karta:,} so‘m"],
            'izoh': ['💵 Naqd:'],
            'admin': [f"{naqd:,} so‘m"]
        })
        summary.to_excel(writer, index=False, header=False, startrow=len(df) + 3)

    return fayl_nomi


def create_daily_excel():
    tz = pytz.timezone('Asia/Tashkent')
    today = datetime.now(tz).date().isoformat()
    oy_nomi = datetime.now(tz).strftime("%B").capitalize()
    sana = datetime.now(tz).strftime("%d_%m_%Y")
    fayl_nomi = f"Tolovlar_{oy_nomi}_{sana}.xlsx"

    fayl = create_excel("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,), fayl_nomi)
    if fayl:
        for admin_id in ADMIN_CHAT_IDS:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                    data={"chat_id": admin_id},
                    files={"document": open(fayl, "rb")}
                )
            except Exception as e:
                print(f"Fayl yuborishda xatolik: {e}")
        print(f"✅ {fayl} yuborildi.")


async def schedule_daily_excel():
    while True:
        tz = pytz.timezone('Asia/Tashkent')
        now = datetime.now(tz)
        next_run = datetime.combine(now.date(), time(23, 59))
        if now > next_run:
            next_run += timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        print(f"⏰ Keyingi Excel {next_run.strftime('%H:%M')} da yaratiladi.")
        await asyncio.sleep(wait_seconds)
        create_daily_excel()


# ---------- TELEGRAM BOT ----------

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
        [InlineKeyboardButton("📊 Oylik hisobotlar", callback_data="oylik_hisobot")]
    ]
    await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat.id

    if user_id not in ADMIN_CHAT_IDS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    if query.data == "today_report":
        create_daily_excel()
        await query.edit_message_text("✅ Bugungi to‘lovlar uchun Excel fayl yaratildi va yuborildi.")

    elif query.data == "oylik_hisobot":
        oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
                 "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
        keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
        await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("month_"):
        oy_nomi = query.data.replace("month_", "")
        sana = datetime.now(pytz.timezone('Asia/Tashkent')).strftime("%Y")
        fayl_nomi = f"Tolovlar_{oy_nomi.capitalize()}_{sana}.xlsx"

        fayl = create_excel("SELECT * FROM tolovlar WHERE lower(oy)=lower(?)", (oy_nomi,), fayl_nomi)
        if fayl:
            for admin_id in ADMIN_CHAT_IDS:
                try:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                        data={"chat_id": admin_id},
                        files={"document": open(fayl, "rb")}
                    )
                except Exception as e:
                    print(f"Fayl yuborishda xatolik: {e}")
            await query.edit_message_text(f"✅ {oy_nomi.capitalize()} oyi uchun Excel fayl yuborildi.")
        else:
            await query.edit_message_text(f"⚠ {oy_nomi.capitalize()} oyi uchun ma'lumot topilmadi.")


async def run_bot():
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(handle_callback))
    print("✅ Bot ishga tushdi.")
    asyncio.create_task(schedule_daily_excel())
    await bot_app.run_polling()


if __name__ == '__main__':
    nest_asyncio.apply()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    asyncio.run(run_bot())

