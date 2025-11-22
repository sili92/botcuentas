# botcuentas

Este bot permite gestionar y consultar **cuentas** mediante comandos como `/get`, usando un archivo JSON para almacenar la información de forma persistente.  
Funciona con `python-telegram-bot 20.7` y está preparado para usarse en Railway.

---

## ⚙️ Archivos necesarios en este repositorio

- `main.cuentas.py`  ← archivo principal del bot  
- `requirements.txt`  
- `.python-version`  
- `README.md`  
- `cuentas.json` (opcional, si no existe el bot lo crea)

---

## 🛠️ Configuración en Railway

En **Settings → Variables**, añade:
BOT_TOKEN = <token de tu bot>
DB_FILE = cuentas.json

---

## ▶️ Start Command en Railway

En **Settings → Start Command**, escribe:


python main.cuentas.py

---

## 📦 Dependencias

Archivo `requirements.txt`:


python-telegram-bot==20.7

Archivo `.python-version`:


3.11.10
