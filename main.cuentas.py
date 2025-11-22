import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

# ===========================
# CONFIGURACIÓN PRINCIPAL
# ===========================

TOKEN = os.getenv("BOT_TOKEN")  # ahora el token se toma de Railway

if not TOKEN:
    raise SystemExit("❌ ERROR: Falta la variable BOT_TOKEN en Railway.")

CUENTAS_FILE = os.getenv("DB_FILE", "cuentas.json")

# Lista exacta de administradores autorizados
ADMIN_IDS = [
    5398217730,
    5890423026,
    7721107311,
    1588416576,
    6093923431,
    1678694654,
    5823910286,
    6719272561
]

# ===========================
# FUNCIONES AUXILIARES
# ===========================

def cargar_cuentas():
    """Carga o crea el archivo JSON de cuentas."""
    if not os.path.exists(CUENTAS_FILE):
        with open(CUENTAS_FILE, "w") as f:
            json.dump({}, f, indent=4)

    with open(CUENTAS_FILE, "r") as f:
        return json.load(f)


def guardar_cuentas(data):
    """Guarda los cambios en el archivo JSON."""
    with open(CUENTAS_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def es_admin_autorizado(update: Update):
    """Verifica si el usuario es uno de los admins permitidos."""
    return update.effective_user.id in ADMIN_IDS

# ===========================
# COMANDO /start
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Usa /acclist para ver las cuentas disponibles o /get <nombre> para solicitar una."
    )

# ===========================
# COMANDO /newacc  (solo admins / privado)
# ===========================
async def newacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != "private":
        await update.message.reply_text("⚠️ Este comando solo puede usarse por privado con el bot.")
        return

    if not await es_admin_autorizado(update):
        await update.message.reply_text("🚫 No tienes permiso para usar este comando.")
        return

    if len(context.args) < 5:
        await update.message.reply_text(
            "Uso: /newacc <nombre> <correo> <contraseña> <usos> <nota>"
        )
        return

    nombre_servicio = context.args[0].capitalize()
    correo = context.args[1]
    contraseña = context.args[2]
    capacidad = context.args[3]

    if not capacidad.isdigit():
        await update.message.reply_text("⚠️ Los usos deben ser un número.")
        return

    capacidad = int(capacidad)
    nota = " ".join(context.args[4:])  # nota con espacios

    data = cargar_cuentas()
    data[nombre_servicio] = {
        "correo": correo,
        "contraseña": contraseña,
        "restantes": capacidad,
        "max": capacidad,
        "nota": nota,
        "creador": user.username or user.first_name or "usuario",
        "creador_id": user.id
    }

    guardar_cuentas(data)

    mensaje = f"""
✅ cuenta agregada con éxito! 

servicio: {nombre_servicio}
correo: {correo}
usos máximos: {capacidad}
añadida por: @{user.username}
nota: {nota}
"""
    await update.message.reply_text(mensaje)

# ===========================
# COMANDO /acclist
# ===========================
async def acclist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = cargar_cuentas()

    if not data:
        await update.message.reply_text("📭 No hay cuentas disponibles.")
        return

    mensaje = "⠀ 𔗨۪ 𝆬  ⠀cuentas gratis disponibles.\n\n"
    for nombre, info in data.items():
        mensaje += f" 𑁯  {nombre} ({info['restantes']} usos restantes)\n"

    mensaje += "\n⏤  puedes solicitar una usando /get + nombre en PRIVADO."

    await update.message.reply_text(mensaje)

# ===========================
# COMANDO /get  (solo privado)
# ===========================
async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != "private":
        await update.message.reply_text("⚠️ Usa este comando en privado conmigo.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Uso: /get <nombre de la cuenta>")
        return

    nombre_servicio = context.args[0].capitalize()
    data = cargar_cuentas()

    if nombre_servicio not in data:
        await update.message.reply_text("❌ No hay una cuenta con ese nombre.")
        return

    cuenta = data[nombre_servicio]

    # restar uso
    cuenta["restantes"] -= 1
    usos_actuales = cuenta["max"] - cuenta["restantes"]

    # borrar cuenta si ya no quedan usos
    if cuenta["restantes"] <= 0:
        del data[nombre_servicio]

    guardar_cuentas(data)

    mensaje = f"""
⠀ઈઉ⠀has solicitado acceso a {nombre_servicio}

𔗨۪ 𝆬   correo: {cuenta['correo']}
𔗨۪ 𝆬   contraseña: {cuenta['contraseña']}
𔗨۪ 𝆬   nota: {cuenta.get('nota', 'sin nota')}
𔗨۪ 𝆬   cuenta by: @{cuenta['creador']}
"""
    await update.message.reply_text(mensaje)

    # notificación al creador
    creador_id = cuenta.get("creador_id")
    if creador_id:
        try:
            await context.bot.send_message(
                chat_id=creador_id,
                text=f"""📩 se solicitó la cuenta que agregaste!

servicio: {nombre_servicio}
correo: {cuenta['correo']}
usos actuales: {usos_actuales} de {cuenta['max']}
solicitado por: @{user.username or user.first_name}"""
            )
        except:
            pass

# ===========================
# COMANDO /removeacc
# ===========================
async def removeacc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type != "private":
        await update.message.reply_text("⚠️ Este comando solo puede usarse en privado.")
        return

    if not await es_admin_autorizado(update):
        await update.message.reply_text("🚫 No tienes permiso para usar este comando.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Uso: /removeacc <nombre>")
        return

    nombre_servicio = context.args[0].capitalize()
    data = cargar_cuentas()

    if nombre_servicio not in data:
        await update.message.reply_text("❌ Esa cuenta no existe.")
        return

    cuenta = data[nombre_servicio]

    if cuenta.get("creador_id") != user.id:
        await update.message.reply_text("🚫 Solo el admin que la subió puede eliminarla.")
        return

    del data[nombre_servicio]
    guardar_cuentas(data)

    mensaje = f"""
✅ cuenta quitada con éxito! 

servicio: {nombre_servicio}
correo: {cuenta['correo']}
usos máximos: {cuenta['max']}
"""
    await update.message.reply_text(mensaje)

# ===========================
# MAIN
# ===========================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newacc", newacc))
    app.add_handler(CommandHandler("acclist", acclist))
    app.add_handler(CommandHandler("get", get))
    app.add_handler(CommandHandler("removeacc", removeacc))

    print("🤖 Bot ejecutándose correctamente...")
    app.run_polling()

if __name__ == "__main__":
    main()
