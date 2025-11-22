# botcuentas

Este bot registra datos en un archivo JSON y envía información formateada a un canal de Telegram.  
Está desarrollado con `python-telegram-bot 20.7` y se ejecuta con polling, por lo que es compatible con Railway.

---

## 🚀 Funciones principales

- Guarda información en un archivo JSON mensual.
- Reenvía mensajes/imágenes al canal configurado.
- Mantiene estadísticas por usuario.
- Comandos:
  - `/refe` → Registrar referencia (respondiendo a una imagen).
  - `/toprefe` → Mostrar top mensual.

---

## 📁 Archivos necesarios en este repositorio

- `main.cuentas.py` ← Archivo principal del bot  
- `requirements.txt`  
- `.python-version`  
- `README.md` ← Este archivo

---

## ⚙️ Configuración en Railway

### 1. Variables de entorno
Configurar en **Settings → Variables**:

