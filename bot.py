from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackContext
from telegram import Update
import sqlite3

TOKEN = "8352843645:AAE40NoWNGJJ71YnxTcfkdLu6ndWOeAyQ2o"

DB = "files.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    caption TEXT
                )""")
    conn.commit()
    conn.close()

def save_file(file_id, caption):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO files (file_id, caption) VALUES (?, ?)", (file_id, caption))
    conn.commit()
    conn.close()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! فایل‌هاتو برام فوروارد کن تا ذخیره کنم.\n"
        "بعد هر وقت خواستی چیزی جستجو کنی، فقط اسمش رو بفرست، اگه باشه برات می‌فرستم."
    )

def handle_files(update: Update, context: CallbackContext):
    msg = update.message
    if msg.document:
        file_id = msg.document.file_id
        caption = msg.caption or msg.document.file_name
    elif msg.video:
        file_id = msg.video.file_id
        caption = msg.caption or "ویدیو"
    elif msg.audio:
        file_id = msg.audio.file_id
        caption = msg.caption or "صوت"
    elif msg.photo:
        file_id = msg.photo[-1].file_id
        caption = msg.caption or "عکس"
    else:
        return

    save_file(file_id, caption)
    msg.reply_text("فایل ذخیره شد ✅")

def search(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT file_id, caption FROM files WHERE caption LIKE ?", (f"%{text}%",))
    results = c.fetchall()
    conn.close()

    if not results:
        update.message.reply_text("چیزی پیدا نشد ❌")
        return

    for file_id, caption in results[:5]:  # حداکثر ۵ تا
        try:
            update.message.reply_document(document=file_id, caption=caption)
        except:
            update.message.reply_text(f"❗ خطا در ارسال فایل: {caption}")

def main():
    init_db()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document | Filters.video | Filters.audio | Filters.photo, handle_files))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, search))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
