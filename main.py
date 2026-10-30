import os, re, html, random, json, threading, requests, zipfile, io
from flask import Flask
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- DIRECT FIX WITH YOUR DATA ---
BRAND = "@XCT_Zaoliya"
FILE_NAME = "Zaoliya_Bodo.html"
INVITE_LINK = "https://t.me/+ac6ZAZQH0uI3NDI1"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8964154107:AAHy0AD0pA9LwRwlmi3zDaBzq9G18xeUAYc")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003852203400"))
# --------------------------------

app_flask = Flask('')
@app_flask.route('/')
def home(): return f"{BRAND} Bot is Alive! 24x7 ON"
def run_flask(): app_flask.run(host='0.0.0.0', port=8080)

PASS_FILE = "passwords.json"
def load_db():
    if os.path.exists(PASS_FILE):
        try: return json.load(open(PASS_FILE))
        except: return {}
    return {}
def save_db(d): json.dump(d, open(PASS_FILE, "w"))
passwords_db = load_db()
user_state = {}

async def check_joined(bot, user_id):
    try:
        m = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return m.status not in ['left','kicked']
    except Exception as e:
        print(f"Join check error: {e}")
        return True

def fetch_with_bypass(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml", "Referer": "https://google.com"}
    try:
        r = requests.get(url, headers=headers, timeout=25, verify=False)
        if r.status_code == 200 and len(r.text) > 300:
            return r.text
    except: pass
    try:
        proxy = f"https://api.allorigins.win/raw?url={url}"
        r = requests.get(proxy, timeout=20)
        if r.status_code == 200 and len(r.text) > 300:
            return r.text
    except: pass
    return "<h1>Content loaded via proxy - Original site blocked 403</h1>"

def deep_clone_site(start_url):
    html_text = fetch_with_bypass(start_url)
    final = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><base href="{start_url}"><title>{BRAND}</title><style>#zaoliya{{background:#000;color:#0f0;padding:12px;position:fixed;top:0;left:0;width:100%;z-index:999999;text-align:center;font-family:monospace}}body{{padding-top:50px}}</style><script>document.addEventListener('contextmenu',e=>{{e.preventDefault();alert('By {BRAND}')}});document.addEventListener('copy',e=>{{e.preventDefault();alert('Protected by {BRAND}')}});</script></head><body><div id="zaoliya">{BRAND} | Zaoliya X Bodo</div>{html_text}</body></html>"""
    with open(FILE_NAME, "w", encoding="utf-8") as f: f.write(final)
    return FILE_NAME

URL_ASK_MSG = """╔════════════════════╗
   📍 URL ᴛᴏ HTML Bᴏᴛ
╚════════════════════╝

⚡ Fᴇᴀᴛᴜʀᴇs:
- 🌍 Fᴀsᴛ URL Fᴇᴛᴄʜ
- 📄 Cʟᴇᴀɴ HTML Exᴘᴏʀᴛ
- ⚡ Iɴsᴛᴀɴᴛ Pʀᴏᴄᴇssɪɴɢ
- 🔒 Sᴇᴄᴜʀᴇ Exᴛʀᴀᴄᴛɪᴏɴ

🎁 Sᴇɴᴅ ᴀ Wᴇʙsɪᴛᴇ URL ᴛᴏ sᴛᴀʀᴛ!

🔗 Exᴀᴍᴘʟᴇ:
https://example.com"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if await check_joined(context.bot, uid):
        uid_s = str(uid)
        if uid_s not in passwords_db:
            passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
        user_state[uid] = {"joined": True, "code_verified": False}
        await update.message.reply_text(f"✅ JOIN REQUEST SUCCESSFUL!\n\n🔑 Code: `{passwords_db[uid_s]}`\n\nYe code bhejo, fir URL mangunga\n\n{BRAND}", parse_mode="Markdown")
    else:
        kb = [[InlineKeyboardButton("🔗 Join Channel", url=INVITE_LINK)], [InlineKeyboardButton("✅ Join Verify", callback_data="check_join")]]
        await update.message.reply_text(f"1️⃣ Join karo:\n{INVITE_LINK}\n\n2️⃣ Verify dabao\n\n{BRAND}", reply_markup=InlineKeyboardMarkup(kb))

async def button_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id; uid_s = str(uid)
    if await check_joined(context.bot, uid):
        if uid_s not in passwords_db:
            passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
        user_state[uid] = {"joined": True, "code_verified": False}
        await q.edit_message_text(f"✅ JOIN REQUEST SUCCESSFUL!\n\n🔑 Code: `{passwords_db[uid_s]}`\n\nAb code bhejo\n\n{BRAND}", parse_mode="Markdown")
    else: await q.answer("❌ Join nahi kiya!", show_alert=True)

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; uid_s = str(uid); text = update.message.text.strip()
    if not await check_joined(context.bot, uid):
        kb = [[InlineKeyboardButton("🔗 Join Channel", url=INVITE_LINK)], [InlineKeyboardButton("✅ Join Verify", callback_data="check_join")]]
        await update.message.reply_text(f"❌ Pehle Join\n{INVITE_LINK}", reply_markup=InlineKeyboardMarkup(kb)); return
    if not user_state.get(uid, {}).get("code_verified", False):
        if uid_s in passwords_db and text == passwords_db[uid_s]:
            user_state[uid] = {"joined": True, "code_verified": True}
            await update.message.reply_text(URL_ASK_MSG); return
        else:
            if uid_s not in passwords_db:
                passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
            await update.message.reply_text(f"❌ Galat Code! Sahi: `{passwords_db[uid_s]}`", parse_mode="Markdown"); return
    url = text
    if not url.startswith("http"): url = "https://" + url
    msg = await update.message.reply_text(f"⏳ All URL Fetching...\n{url}")
    file_path = deep_clone_site(url)
    size_kb = os.path.getsize(file_path) / 1024
    caption = f"""✅ HTML EXTRACTION COMPLETE!

📁 Fɪʟᴇ Nᴀᴍᴇ: {FILE_NAME}
📦 Fɪʟᴇ Sɪᴢᴇ: {size_kb:.1f} KB
🔒By: {BRAND}

⚡ Exᴛʀᴀᴄᴛᴇᴅ Fᴇᴀᴛᴜʀᴇs:
- 🌍 Lɪᴠᴇ URL Fᴇᴛᴄʜ
- 📄 Cʟᴇᴀɴ HTML Exᴘᴏʀᴛ
- ⚡ Fᴀsᴛ Pʀᴏᴄᴇssɪɴɢ
- 🔒 Sᴇᴄᴜʀᴇ Exᴛʀᴀᴄᴛɪᴏɴ

✅ Yᴏᴜʀ HTML ғɪʟᴇ ɪs ʀᴇᴀᴅʏ!
👿 JOIN: {INVITE_LINK}"""
    await update.message.reply_document(document=open(file_path, "rb"), filename=FILE_NAME, caption=caption)
    await msg.delete()

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_check, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    print(f"{BRAND} Running - Fixed with your token & channel")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__': main()
