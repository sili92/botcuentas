# main.cuentas.py
import os
import json
import html
import logging
import threading
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)

# CONFIG
BOT_TOKEN = os.getenv("BOT_TOKEN")
DESTINATION_CHAT_ID = os.getenv("DESTINATION_CHAT_ID")  # opcional
DB_FILE = os.getenv("DB_FILE", "cuentas.json")

if not BOT_TOKEN:
    log.error("❌ BOT_TOKEN missing in environment. Add BOT_TOKEN and restart.")
    raise SystemExit(1)

# intentar convertir DESTINATION_CHAT_ID a int si existe
if DESTINATION_CHAT_ID:
    try:
        DESTINATION_CHAT_ID = int(DESTINATION_CHAT_ID)
        log.info("DESTINATION_CHAT_ID detectado en variables de entorno.")
    except Exception:
        log.info("DESTINATION_CHAT_ID es un string (por ejemplo @channel) o no convertible a int; se usará tal cual.")
else:
    log.info("DESTINATION_CHAT_ID no provisto — el bot NO reenviará a canal automáticamente (comportamiento por defecto).")

FILE_LOCK = threading.Lock()

def month_now():
    return datetime.now().strftime("%Y-%m")

def load_json(path):
    with FILE_LOCK:
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            log.warning("JSON corrupto: %s — re-inicializando.", path)
            return {}
        except Exception as e:
            log.exception("Error leyendo JSON %s: %s", path, e)
            return {}

def save_json(path, data):
    with FILE_LOCK:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.exception("Error guardando JSON %s: %s", path, e)

# HANDLERS
async def refe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Responde a una imagen con /refe.")
        return

    replied = update.message.reply_to_message
    if not replied.photo:
        await update.message.reply_text("⚠️ Solo se aceptan imágenes.")
        return

    img_user = replied.from_user
    uid = str(img_user.id)
    uname = img_user.username or img_user.first_name

    data = load_json(DB_FILE)
    mes = month_now()
    if mes not in data:
        data[mes] = {}
    if uid not in data[mes]:
        data[mes][uid] = {"username": uname, "count": 0}

    data[mes][uid]["count"] += 1
    data[mes][uid]["username"] = uname
    save_json(DB_FILE, data)

    time = replied.date.strftime("%H:%M:%S")
    caption_original = html.escape(replied.caption or "")
    photo_file = replied.photo[-1].file_id

    formatted = (
        f"📌 Nueva cuenta/entrada\n"
        f"👤 @{uname}\n"
        f"🆔 {uid}\n"
        f"🕒 {time}\n"
        f"💬 {caption_original}"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("INFO", url="https://example.com"),
         InlineKeyboardButton("OWNER", url="https://t.me/zilbato")]
    ])

    # Si DESTINATION_CHAT_ID existe, intentamos enviar al canal; si no, enviamos confirmación local
    if DESTINATION_CHAT_ID:
        try:
            await context.bot.send_photo(
                chat_id=DESTINATION_CHAT_ID,
                photo=photo_file,
                caption=formatted,
                parse_mode="HTML",
                reply_markup=keyboard
            )
            await update.message.reply_text("✅ Registrado y reenviado al canal.")
            log.info("Reenviada imagen al canal %s (autor=%s)", DESTINATION_CHAT_ID, uname)
            return
        except Exception as e:
            log.exception("Error reenviando al canal %s: %s", DESTINATION_CHAT_ID, e)
            # caemos al comportamiento de fallback: confirmar en chat
            await update.message.reply_text("⚠️ Registrado pero falló el reenvío al canal. Comprobando permisos.")
            return

    # fallback: no hay canal configurado, solo confirmamos en el chat
    await update.message.reply_text("✅ Referencia registrada (no hay canal configurado).")

async def toprefe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_json(DB_FILE)
    mes = month_now()
    if mes not in data or not data[mes]:
        await update.message.reply_text("📭 No hay entradas este mes.")
        return
    orden = sorted(data[mes].values(), key=lambda x: x.get("count", 0), reverse=True)
    text = f"🏆 TOP — {mes}\n\n"
    for i, u in enumerate(orden[:10], 1):
        text += f"{i}. @{u.get('username','desconocido')}: {u.get('count',0)}\n"
    await update.message.reply_text(text, parse_mode="HTML")

def main():
    log.info("Iniciando bot cuentas...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("refe", refe))
    app.add_handler(CommandHandler("toprefe", toprefe))
    app.run_polling()

if __name__ == "__main__":
    main()
    
