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
# BOT_TOKEN = '7935396412:AAFhVBQ1NNmw-giNGacreQkS71bsFlZAmM8'
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
#             f"💰 To‘lov: {tolov} so‘m\n"
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
#         cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(
#                 f"📅 *{today}* kuni hech qanday to‘lov yo‘q. Excel fayl yaratilmadi.",
#                 parse_mode="Markdown"
#             )
#             return

#         total_sum = sum(row[2] for row in rows)
#         await query.edit_message_text(
#             f"📅 *{today}* kuni jami to‘lov: *{total_sum:,}* so‘m",
#             parse_mode="Markdown"
#         )

#         df = pd.DataFrame(
#             rows,
#             columns=['id', 'ismi', 'tolov', 'kurs', 'oy', 'izoh', 'admin', 'oqituvchi', 'vaqt', 'tolov_turi']
#         )

#         os.makedirs("reports", exist_ok=True)

#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy].copy()

#             # ✅ Oxirida Jami, Naqd, Klik qo‘shish
#             oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

#             jami_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Jami to‘lov'],
#                 'tolov': [oy_df['tolov'].sum()],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
#             klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

#             naqd_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Naqd'],
#                 'tolov': [naqd_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })
#             klik_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Klik'],
#                 'tolov': [klik_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"

#             try:
#                 oy_df.to_excel(file_path, index=False)
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         with open(file_path, 'rb') as f:
#                             await context.bot.send_document(
#                                 chat_id=admin_id,
#                                 document=f,
#                                 caption=f"{oy.capitalize()} oyi - {today}"
#                             )
#                     except Exception as e:
#                         print(f"Failed to send document to admin {admin_id}: {e}")
#             except Exception as e:
#                 print(f"Failed to generate Excel for {oy}: {e}")
#                 await context.bot.send_message(
#                     chat_id=user_id,
#                     text=f"Excel fayl yaratishda xato: {oy}"
#                 )

#     elif query.data == "oylik_menyu":
#         oylar = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
#                  "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"]
#         keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
#         reply_markup = InlineKeyboardMarkup(keyboard)
#         await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

#     # elif query.data.startswith("month_"):
#     #     oy_nomi = query.data.replace("month_", "")
#     #     con = sqlite3.connect(DB_PATH)
#     #     cur = con.cursor()
#     #     cur.execute("SELECT tolov FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
#     #     rows = cur.fetchall()
#     #     con.close()

#     #     if not rows:
#     #         await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#     #         return

#     #     total_sum = sum(row[0] for row in rows)
#     #     await query.edit_message_text(
#     #         f"🗓 *{oy_nomi.capitalize()}* oyi uchun jami to‘lov: *{total_sum:,}* so‘m",
#     #         parse_mode="Markdown"
#     #     )
#     elif query.data.startswith("month_"):
#         oy_nomi = query.data.replace("month_", "")
#         con = sqlite3.connect(DB_PATH)
#         cur = con.cursor()
#         cur.execute("SELECT tolov, tolov_turi FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
#         rows = cur.fetchall()
#         con.close()

#         if not rows:
#             await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
#             return

#         # Hisoblash
#         jami_sum = sum(row[0] for row in rows)
#         naqd_sum = sum(row[0] for row in rows if str(row[1]).lower() == "naqd")
#         karta_sum = sum(row[0] for row in rows if str(row[1]).lower() in ["klik", "click", "karta", "card"])

#         text = (
#             f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n"
#             f"💵 Naqd: {naqd_sum:,} so‘m\n"
#             f"💳 Karta: {karta_sum:,} so‘m\n"
#             f"📊 Jami: {jami_sum:,} so‘m"
#         )

#         await query.edit_message_text(text, parse_mode="Markdown")



# async def send_daily_report(context: CallbackContext):
#     today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
#     con = sqlite3.connect(DB_PATH)
#     df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", con, params=(today,))
#     con.close()

#     if df.empty:
#         for admin_id in ADMIN_CHAT_IDS:
#             try:
#                 await context.bot.send_message(chat_id=admin_id, text=f"📅 {today} kuni hech qanday to‘lov bo‘lmadi.")
#             except Exception as e:
#                 print(f"Failed to send empty report message to admin {admin_id}: {e}")
#     else:
#         os.makedirs("reports", exist_ok=True)
#         for oy in df['oy'].unique():
#             oy_df = df[df['oy'] == oy].copy()

#             # ✅ Oxirida Jami, Naqd, Klik qo‘shish
#             oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

#             jami_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Jami to‘lov'],
#                 'tolov': [oy_df['tolov'].sum()],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             naqd_sum = oy_df.loc[oy_df['tolov_turi'] == 'naqd', 'tolov'].sum()
#             klik_sum = oy_df.loc[oy_df['tolov_turi'].isin(['klik', 'click']), 'tolov'].sum()

#             naqd_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Naqd'],
#                 'tolov': [naqd_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })
#             klik_row = pd.DataFrame({
#                 'id': [''],
#                 'ismi': ['Klik'],
#                 'tolov': [klik_sum],
#                 'kurs': [''],
#                 'oy': [''],
#                 'izoh': [''],
#                 'admin': [''],
#                 'oqituvchi': [''],
#                 'vaqt': [''],
#                 'tolov_turi': ['']
#             })

#             oy_df = pd.concat([oy_df, jami_row, naqd_row, klik_row], ignore_index=True)

#             file_path = f"reports/hisobot_{today}_{oy}.xlsx"

#             try:
#                 oy_df.to_excel(file_path, index=False)
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         with open(file_path, 'rb') as f:
#                             await context.bot.send_document(
#                                 chat_id=admin_id,
#                                 document=f,
#                                 caption=f"{oy.capitalize()} oyi - {today}"
#                             )
#                     except Exception as e:
#                         print(f"Failed to send document to admin {admin_id}: {e}")
#             except Exception as e:
#                 print(f"Failed to generate Excel for {oy}: {e}")
#                 for admin_id in ADMIN_CHAT_IDS:
#                     try:
#                         await context.bot.send_message(
#                             chat_id=admin_id,
#                             text=f"Excel fayl yaratishda xato: {oy}"
#                         )
#                     except Exception as e:
#                         print(f"Failed to send error message to admin {admin_id}: {e}")


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
#     threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
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
    ConversationHandler,
    MessageHandler,
    filters
)

app = Flask(__name__)
DB_PATH = 'crm.db'
BOT_TOKEN = '7935396412:AAFhVBQ1NNmw-giNGacreQkS71bsFlZAmM8'

# ------------------------- ADMIN VA SUPER ADMIN
SUPER_ADMIN_IDS = [6855997739]  # Super adminlar
ADMIN_CHAT_IDS = [6855997739, 266123144, 1657599027, 6449680789]  # Oddiy adminlar

# ------------------------- DATABASE
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

# ------------------------- FLASK ROUTE
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

# ------------------------- TELEGRAM BOT
# --- start
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ADMIN_CHAT_IDS:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
        [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
    ]

    # Super admin qo'shimcha tugmalar
    if user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("✏️ Bitta talaba summasini o‘zgartirish", callback_data="super_change_single")])
        keyboard.append([InlineKeyboardButton("📌 Oy bo‘yicha jami summani o‘zgartirish", callback_data="super_change_month")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=reply_markup)

# --- Hisobotlar va tugmalar
async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat.id

    if user_id not in ADMIN_CHAT_IDS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    # --- Bugungi hisobot
    if query.data == "today_report":
        today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt) = ?", (today,))
        rows = cur.fetchall()
        con.close()
        if not rows:
            await query.edit_message_text(f"📅 *{today}* kuni hech qanday to‘lov yo‘q.", parse_mode="Markdown")
            return
        total_sum = sum(row[2] for row in rows)
        await query.edit_message_text(f"📅 *{today}* kuni jami to‘lov: *{total_sum:,}* so‘m", parse_mode="Markdown")

    # --- Oy bo'yicha hisobot
    elif query.data == "oylik_menyu":
        oylar = ["Yanvar","Fevral","Mart","Aprel","May","Iyun",
                 "Iyul","Avgust","Sentyabr","Oktyabr","Noyabr","Dekabr"]
        keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=reply_markup)

    elif query.data.startswith("month_"):
        oy_nomi = query.data.replace("month_", "")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT tolov, tolov_turi FROM tolovlar WHERE lower(oy) = ?", (oy_nomi,))
        rows = cur.fetchall()
        con.close()
        if not rows:
            await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
            return
        jami_sum = sum(row[0] for row in rows)
        naqd_sum = sum(row[0] for row in rows if str(row[1]).lower() == "naqd")
        karta_sum = sum(row[0] for row in rows if str(row[1]).lower() in ["klik","click","karta","card"])
        text = f"🗓 *{oy_nomi.capitalize()}* oyi uchun to‘lovlar:\n\n💵 Naqd: {naqd_sum:,} so‘m\n💳 Karta: {karta_sum:,} so‘m\n📊 Jami: {jami_sum:,} so‘m"
        await query.edit_message_text(text, parse_mode="Markdown")

# ------------------------- SUPER ADMIN FUNKSIYALARI
STATE_USER = 1
STATE_OLD_MONTH = 2
STATE_NEW_MONTH = 3
STATE_NEW_AMOUNT = 4
STATE_MONTH_TOTAL = 5
STATE_MONTH_TOTAL_AMOUNT = 6

def update_single_payment_and_month(talaba_ismi, eski_oy, yangi_oy, yangi_tolov):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        UPDATE tolovlar
        SET oy = ?, tolov = ?
        WHERE ismi = ? AND lower(oy) = ?
    """, (yangi_oy, yangi_tolov, talaba_ismi, eski_oy.lower()))
    con.commit()
    con.close()

def update_month_total(oy, yangi_jami):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id, tolov FROM tolovlar WHERE lower(oy) = ?", (oy.lower(),))
    rows = cur.fetchall()
    if not rows:
        con.close()
        return False
    total_old = sum(r[1] for r in rows)
    for r in rows:
        prop = r[1] / total_old if total_old else 0
        new_val = round(prop * yangi_jami)
        cur.execute("UPDATE tolovlar SET tolov = ? WHERE id = ?", (new_val, r[0]))
    con.commit()
    con.close()
    return True

# --- Bitta talaba o'zgartirish
async def start_change_single(update: Update, context: CallbackContext):
    if update.effective_chat.id not in SUPER_ADMIN_IDS:
        await update.message.reply_text("Siz super admin emassiz, bu funksiyani ishlata olmaysiz.")
        return ConversationHandler.END
    await update.message.reply_text("Talaba ismini kiriting:")
    return STATE_USER

async def get_user(update: Update, context: CallbackContext):
    context.user_data['talaba'] = update.message.text
    await update.message.reply_text("Qaysi oyni o‘zgartirmoqchisiz? (eski oy)")
    return STATE_OLD_MONTH

async def get_old_month(update: Update, context: CallbackContext):
    context.user_data['eski_oy'] = update.message.text
    await update.message.reply_text("Yangi oy nomini kiriting:")
    return STATE_NEW_MONTH

async def get_new_month(update: Update, context: CallbackContext):
    context.user_data['yangi_oy'] = update.message.text
    await update.message.reply_text("Yangi summani kiriting:")
    return STATE_NEW_AMOUNT

async def get_new_amount(update: Update, context: CallbackContext):
    try:
        yangi_tolov = int(update.message.text)
    except:
        await update.message.reply_text("Iltimos faqat raqam kiriting.")
        return STATE_NEW_AMOUNT

    talaba = context.user_data['talaba']
    eski_oy = context.user_data['eski_oy']
    yangi_oy = context.user_data['yangi_oy']

    update_single_payment_and_month(talaba, eski_oy, yangi_oy, yangi_tolov)
    await update.message.reply_text(
        f"{talaba} ning {eski_oy} oyi yozuvi yangilandi.\nYangi oy: {yangi_oy}\nYangi summa: {yangi_tolov}"
    )
    return ConversationHandler.END

single_change_handler = ConversationHandler(
    entry_points=[CommandHandler('change_single', start_change_single)],
    states={
        STATE_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_user)],
        STATE_OLD_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_old_month)],
        STATE_NEW_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_month)],
        STATE_NEW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_new_amount)],
    },
    fallbacks=[]
)

# --- Oy bo'yicha jami summani o'zgartirish
async def start_change_month(update: Update, context: CallbackContext):
    if update.effective_chat.id not in SUPER_ADMIN_IDS:
        await update.message.reply_text("Siz super admin emassiz, bu funksiyani ishlata olmaysiz.")
        return ConversationHandler.END
    await update.message.reply_text("Qaysi oy jami summasini o‘zgartirmoqchisiz?")
    return STATE_MONTH_TOTAL

async def get_month(update: Update, context: CallbackContext):
    context.user_data['oy'] = update.message.text
    await update.message.reply_text("Yangi jami summani kiriting:")
    return STATE_MONTH_TOTAL_AMOUNT

async def get_month_total_amount(update: Update, context: CallbackContext):
    try:
        yangi_jami = int(update.message.text)
    except:
        await update.message.reply_text("Iltimos faqat raqam kiriting.")
        return STATE_MONTH_TOTAL_AMOUNT

    oy = context.user_data['oy']
    success = update_month_total(oy, yangi_jami)
    if not success:
        await update.message.reply_text(f"{oy} oyi uchun yozuv topilmadi.")
        return ConversationHandler.END

    await update.message.reply_text(f"{oy} oyi bo‘yicha jami to‘lovlar yangilandi. Yangi jami summa: {yangi_jami}")
    return ConversationHandler.END

month_total_handler = ConversationHandler(
    entry_points=[CommandHandler('change_month_total', start_change_month)],
    states={
        STATE_MONTH_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_month)],
        STATE_MONTH_TOTAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_month_total_amount)],
    },
    fallbacks=[]
)

# ------------------------- RUN BOT
async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.add_handler(single_change_handler)
    app_bot.add_handler(month_total_handler)
    app_bot.job_queue.run_daily(lambda ctx: send_daily_report(ctx), time=dtime(hour=23, minute=59, tzinfo=pytz.timezone('Asia/Tashkent')))
    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()

# ------------------------- MAIN
if __name__ == '__main__':
    import threading
    nest_asyncio.apply()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    asyncio.run(run_bot())
