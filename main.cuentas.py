# main.lastbot.py
import os
import json
import html
import logging
import threading
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------------- logging ----------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# ---------------- config from env ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT_ID = os.getenv("DESTINATION_CHAT_ID")  # can be -100... or @channelusername
DB_FILE = os.getenv("DB_FILE", "data_lastbot.json")    # default file name

if not BOT_TOKEN:
    log.error("❌ BOT_TOKEN not found in environment. Set BOT_TOKEN and restart.")
    raise SystemExit(1)

if not DESTINATION_CHAT_ID:
    log.error("❌ DESTINATION_CHAT_ID not found in environment. Set DESTINATION_CHAT_ID and restart.")
    raise SystemExit(1)

# try convert chat id to int
try:
    DESTINATION_CHAT_ID = int(DESTINATION_CHAT_ID)
except Exception:
    # keep as string if not int (e.g., @channelname)
    pass

# ---------------- file lock ----------------
FILE_LOCK = threading.Lock()

# ---------------- helpers ----------------
def now_month():
    return datetime.now().strftime("%Y-%m")

def safe_load_json(path):
    with FILE_LOCK:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log.warning("JSON file corrupted or empty, reinitializing: %s", path)
            return {}
        except Exception as e:
            log.exception("Error reading JSON file %s: %s", path, e)
            return {}

def safe_save_json(path, data):
    with FILE_LOCK:
        try:
            # ensure dir exists
            d = os.path.dirname(path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.exception("Error saving JSON file %s: %s", path, e)

# ---------------- bot handlers ----------------
# Example handler: /sendref (adapt to your bot's logic)
async def sendref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Example command that expects the user to reply to a photo.
    It saves counting data in JSON and forwards formatted message to DESTINATION_CHAT_ID.
    """
    try:
        await update.message.reply_text("✅ Comando recibido.")
    except Exception:
        pass

    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Responde a una imagen con este comando.")
        return

    replied = update.message.reply_to_message
    if not replied.photo:
        await update.message.reply_text("⚠️ Solo están permitidas imágenes. Responde a una imagen.")
        return

    # author of the image
    img_user = replied.from_user
    img_id = str(img_user.id)
    img_name = img_user.username or img_user.first_name

    # load data, update counts grouped by month
    data = safe_load_json(DB_FILE)
    month = now_month()
    if month not in data:
        data[month] = {}

    if img_id not in data[month]:
        data[month][img_id] = {"username": img_name, "count": 0}

    data[month][img_id]["count"] += 1
    data[month][img_id]["username"] = img_name
    safe_save_json(DB_FILE, data)

    # prepare formatted message
    time_str = replied.date.strftime("%I:%M:%S %p")
    caption = replied.caption or ""
    caption = html.escape(caption)
    photo_file_id = replied.photo[-1].file_id

    formatted = (
        f"📌 Nueva referencia\n"
        f"Usuario: @{img_name}\n"
        f"ID: {img_id}\n"
        f"Hora: {time_str}\n"
        f"Texto: {caption}\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Info", url="https://example.com"),
         InlineKeyboardButton("Owner", url="https://t.me/your_owner")]
    ])

    try:
        await context.bot.send_photo(
            chat_id=DESTINATION_CHAT_ID,
            photo=photo_file_id,
            caption=formatted,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        log.info("Forwarded image by %s to %s", img_name, DESTINATION_CHAT_ID)
    except Exception as e:
        log.exception("Failed sending photo to destination: %s", e)
        await update.message.reply_text("❌ Error al enviar al canal.")

# Example stats command: /topmonth
async def topmonth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = safe_load_json(DB_FILE)
    month = now_month()
    if month not in data or not data[month]:
        await update.message.reply_text("No hay referencias este mes.")
        return
    top = sorted(data[month].values(), key=lambda x: x.get("count", 0), reverse=True)
    text = f"🏆 TOP - {month}\n\n"
    for i, u in enumerate(top[:10], 1):
        text += f"{i}. @{u.get('username','desconocido')}: {u.get('count',0)} refs\n"
    await update.message.reply_text(text, parse_mode="HTML")

# ---------------- main ----------------
def main() -> None:
    log.info("Starting last bot...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # register handlers (change names to match your bot)
    app.add_handler(CommandHandler("sendref", sendref))
    app.add_handler(CommandHandler("topmonth", topmonth))

    log.info("Bot initialized, running polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
