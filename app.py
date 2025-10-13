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
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

app = Flask(__name__)
DB_PATH = 'crm.db'
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Super admin va oddiy adminlarni alohida saqlaymiz
SUPER_ADMIN_IDS = [6855997739]  # faqat super admin
ORDINARY_ADMIN_IDS = [266123144, 1657599027, 1725877539]  # oddiy adminlar
ALL_ADMINS = SUPER_ADMIN_IDS + ORDINARY_ADMIN_IDS

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
            f"💰 To‘lov: {tolov} so‘m\n"
            f"📚 Kurs: {kurs} ({oy} oyi)\n"
            f"💳 To‘lov turi: {tolov_turi}\n"
            f"👨‍🏫 O‘qituvchi: {oqituvchi}\n"
            f"🛠 Admin: {admin}\n"
            f"💬 Izoh: {izoh or 'Yo‘q'}\n"
            f"🕒 Sana: {vaqt}"
        )

        for admin_id in ALL_ADMINS:
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


async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if user_id not in ALL_ADMINS:
        await update.message.reply_text("Siz admin emassiz.")
        return

    keyboard = [
        [InlineKeyboardButton("📅 Bugungi to‘lovlar", callback_data="today_report")],
        [InlineKeyboardButton("📊 Oylik to‘lovlar", callback_data="oylik_menyu")]
    ]
    if user_id in SUPER_ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("⚙️ Super admin panel", callback_data="super_admin")])

    await update.message.reply_text("Xush kelibsiz, admin! Tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.message.chat.id

    if user_id not in ALL_ADMINS:
        await query.edit_message_text("Siz admin emassiz.")
        return

    today = datetime.now(pytz.timezone('Asia/Tashkent')).date().isoformat()

    if query.data == "today_report":
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM tolovlar WHERE DATE(vaqt)=?", (today,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text(f"📅 *{today}* kuni hech qanday to‘lov yo‘q.", parse_mode="Markdown")
            return

        df = pd.DataFrame(rows, columns=['id','ismi','tolov','kurs','oy','izoh','admin','oqituvchi','vaqt','tolov_turi'])
        os.makedirs("reports", exist_ok=True)
        for oy in df['oy'].unique():
            oy_df = df[df['oy']==oy].copy()
            oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

            jami_row = pd.DataFrame({'id':[''],'ismi':['Jami to‘lov'],'tolov':[oy_df['tolov'].sum()],
                                     'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
            naqd_row = pd.DataFrame({'id':[''],'ismi':['Naqd'],'tolov':[oy_df.loc[oy_df['tolov_turi']=='naqd','tolov'].sum()],
                                     'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
            klik_row = pd.DataFrame({'id':[''],'ismi':['Klik'],'tolov':[oy_df.loc[oy_df['tolov_turi'].isin(['klik','click']),'tolov'].sum()],
                                     'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
            oy_df = pd.concat([oy_df,jami_row,naqd_row,klik_row], ignore_index=True)

            file_path = f"reports/hisobot_{today}_{oy}.xlsx"
            oy_df.to_excel(file_path, index=False)

            for admin_id in ALL_ADMINS:
                try:
                    with open(file_path,'rb') as f:
                        await context.bot.send_document(chat_id=admin_id, document=f, caption=f"{oy.capitalize()} oyi - {today}")
                except Exception as e:
                    print(f"Failed to send document to admin {admin_id}: {e}")

        await query.edit_message_text(f"📅 Bugungi to‘lovlar Excel fayl sifatida yuborildi.")


    elif query.data == "oylik_menyu":
        oylar = ["Yanvar","Fevral","Mart","Aprel","May","Iyun","Iyul","Avgust","Sentyabr","Oktyabr","Noyabr","Dekabr"]
        keyboard = [[InlineKeyboardButton(f"🗓 {oy}", callback_data=f"month_{oy.lower()}")] for oy in oylar]
        await query.edit_message_text("Oy bo‘yicha hisobotni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))


    elif query.data.startswith("month_"):
        oy_nomi = query.data.replace("month_","")
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT tolov,tolov_turi FROM tolovlar WHERE lower(oy)=?", (oy_nomi,))
        rows = cur.fetchall()
        con.close()

        if not rows:
            await query.edit_message_text(f"{oy_nomi.capitalize()} oyi uchun to‘lovlar topilmadi.")
            return

        df = pd.DataFrame(rows, columns=['tolov','tolov_turi'])
        jami_sum = df['tolov'].sum()
        naqd_sum = df.loc[df['tolov_turi']=='naqd','tolov'].sum()
        klik_sum = df.loc[df['tolov_turi'].isin(['klik','click']),'tolov'].sum()
        message = f"📊 {oy_nomi.capitalize()} oyi:\n\n💰 Jami: {jami_sum}\n🖱 Click: {klik_sum}\n💵 Naqd: {naqd_sum}"

        if user_id in ORDINARY_ADMIN_IDS:
            await query.edit_message_text(message)
        else:
            os.makedirs("reports",exist_ok=True)
            jami_row = pd.DataFrame({'tolov':[jami_sum],'tolov_turi':['Jami to‘lov']})
            naqd_row = pd.DataFrame({'tolov':[naqd_sum],'tolov_turi':['Naqd']})
            klik_row = pd.DataFrame({'tolov':[klik_sum],'tolov_turi':['Klik']})
            df_excel = pd.concat([df,jami_row,naqd_row,klik_row],ignore_index=True)
            file_path = f"reports/hisobot_{oy_nomi}_{today}.xlsx"
            df_excel.to_excel(file_path,index=False)
            for admin_id in ALL_ADMINS:
                try:
                    with open(file_path,'rb') as f:
                        await context.bot.send_document(chat_id=admin_id, document=f, caption=f"{oy_nomi.capitalize()} oyi")
                except Exception as e:
                    print(f"Failed to send document to admin {admin_id}: {e}")
            keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="oylik_menyu")]]
            await query.edit_message_text(f"🗓 {oy_nomi.capitalize()} oyi Excel fayl sifatida yuborildi.", reply_markup=InlineKeyboardMarkup(keyboard))


async def send_daily_report(context: CallbackContext):
    today = datetime.now(pytz.timezone('Asia/Tashkent')).strftime('%Y-%m-%d')
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tolovlar WHERE DATE(vaqt)=?", con, params=(today,))
    con.close()

    if df.empty:
        for admin_id in ALL_ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=f"📅 {today} kuni hech qanday to‘lov bo‘lmadi.")
        return

    os.makedirs("reports", exist_ok=True)
    for oy in df['oy'].unique():
        oy_df = df[df['oy']==oy].copy()
        oy_df['tolov_turi'] = oy_df['tolov_turi'].astype(str).str.lower()

        jami_row = pd.DataFrame({'id':[''],'ismi':['Jami to‘lov'],'tolov':[oy_df['tolov'].sum()],
                                 'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
        naqd_row = pd.DataFrame({'id':[''],'ismi':['Naqd'],'tolov':[oy_df.loc[oy_df['tolov_turi']=='naqd','tolov'].sum()],
                                 'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
        klik_row = pd.DataFrame({'id':[''],'ismi':['Klik'],'tolov':[oy_df.loc[oy_df['tolov_turi'].isin(['klik','click']),'tolov'].sum()],
                                 'kurs':[''],'oy':[''],'izoh':[''],'admin':[''],'oqituvchi':[''],'vaqt':[''],'tolov_turi':['']})
        oy_df = pd.concat([oy_df,jami_row,naqd_row,klik_row], ignore_index=True)

        file_path = f"reports/hisobot_{today}_{oy}.xlsx"
        oy_df.to_excel(file_path,index=False)

        for admin_id in ALL_ADMINS:
            try:
                with open(file_path,'rb') as f:
                    await context.bot.send_document(chat_id=admin_id, document=f, caption=f"{oy.capitalize()} oyi - {today}")
            except Exception as e:
                print(f"Failed to send document to admin {admin_id}: {e}")


async def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(handle_callback))
    app_bot.job_queue.run_daily(send_daily_report, time=dtime(hour=23,minute=59,tzinfo=pytz.timezone('Asia/Tashkent')))
    print("✅ Bot ishga tushdi.")
    await app_bot.run_polling()


if __name__ == '__main__':
    import threading
    nest_asyncio.apply()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    asyncio.run(run_bot())
