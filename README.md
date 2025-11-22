# botcuentas

Este bot permite gestionar y consultar **cuentas** mediante comandos como `/get`, usando un archivo JSON para almacenar la información de forma persistente.  
Funciona con `python-telegram-bot 20.7` y está preparado para usarse en Railway.

---
## ⚙️ Archivos necesarios en este repositorio

- `main.cuentas.py`  ← archivo principal del bot  
- `requirements.txt`  
- `.python-version`  
- `README.md`  ← este archivo  
- `cuentas.json` (opcional, si no existe el bot lo crea)

---
## 🛠️ Configuración en Railway

En **Settings → Variables**, añade:

BOT_TOKEN = <token de tu bot>
DB_FILE = cuentas.json
DESTINATION_CHAT_ID = <id si tu bot envía mensajes a un canal> # opcional

yaml
Copiar código

---

## ▶️ Start Command en Railway

En **Settings → Start Command**, escribe:

python main.cuentas.py

yaml
Copiar código

---

## 📦 Dependencias

Archivo `requirements.txt`:

python-telegram-bot==20.7

go
Copiar código

Archivo `.python-version`:

3.11.10

yaml
Copiar código

---

## ▶️ Ejecución local (opcional)

pip install -r requirements.txt
python main.cuentas.py

yaml
Copiar código

---

## 📝 Notas
- Este bot NO funciona con fotos ni referencias; es un bot de **cuentas /get**.  
- El archivo JSON se crea automáticamente si no existe.  
- Railway lo ejecuta en modo **polling**, por lo que no necesita puertos ni webhooks.

- Este bot NO funciona con fotos ni referencias; es un bot de **cuentas /get**.  
- El archivo JSON se crea automáticamente si no existe.  
- Railway lo ejecuta en modo **polling**, por lo que no necesita puertos ni webhooks.
