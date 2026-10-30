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
        # Simple obfuscate - make it downloadable
        filename = "Zaoliya_HTML.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filename
    except Exception as e:
        print(f"Clone error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to URL to HTML Bot!\n\n"
        "🔗 Send me any Website URL\n"
        "📄 I will give you HTML file instantly!\n\n"
        "Example: https://google.com"
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not re.match(r'^https?://', text):
        await update.message.reply_text("❌ Please send a valid URL starting with http:// or https://\nExample: https://example.com")
        return
    
    await update.message.reply_text("⏳ Downloading HTML... Please wait 5-10 sec")
    
    loop = asyncio.get_event_loop()
    file_path = await loop.run_in_executor(None, deep_clone_site, text)
    
    if file_path and os.path.exists(file_path):
        await update.message.reply_document(
            document=open(file_path, 'rb'),
            filename=os.path.basename(file_path),
            caption=f"✅ HTML DONE!\n🔗 URL: {text}"
        )
        try:
            os.remove(file_path)
        except:
            pass
    else:
        await update.message.reply_text("❌ Failed to get HTML. Try another URL or check if site blocks bot.")

def main():
    print("@XCT_Zaoliya Running - Direct URL to HTML Mode - No Channel Check")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Run Flask in thread for Render health check
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Bot polling started...")
    app.run_polling()

if __name__ == '__main__':
    main()
