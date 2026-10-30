
import os
import re
import asyncio
import threading
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8964154107:AAG_J2KXOY4v4wNvWPMev7hcy8K0zaGdBrk")

app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "URL to HTML Bot 24x7 - Direct Mode - Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

def deep_clone_site(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
        html_content = r.text
        filename = "Zaoliya_HTML.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filename
    except Exception as e:
        print(f"Clone error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! Send any Website URL and I will give you HTML file!\n\nExample: https://google.com"
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not re.match(r'^https?://', text):
        await update.message.reply_text("❌ Send valid URL like https://example.com")
        return
    await update.message.reply_text("⏳ Downloading HTML... wait 5 sec")
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, deep_clone_site, text)
    if file_path and os.path.exists(file_path):
        await update.message.reply_document(
            document=open(file_path, 'rb'),
            filename=os.path.basename(file_path),
            caption=f"✅ HTML DONE! URL: {text}"
        )
        try:
            os.remove(file_path)
        except:
            pass
    else:
        await update.message.reply_text("❌ Failed! Try another URL")

def main():
    # FIX FOR RENDER - Create event loop for MainThread
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except:
        pass
    
    print("Zaoliya Running - Direct URL to HTML - Fixed Event Loop")
    
    # Start Flask in background thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    print("Bot polling started...")
    app.run_polling()

if __name__ == '__main__':
    main()
