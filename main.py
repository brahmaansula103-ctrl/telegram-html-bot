import os, random, json, threading, requests, asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BRAND = "@XCT_Zaoliya"
FILE_NAME = "Zaoliya_Bodo.html"
INVITE_LINK = "https://t.me/+ac6ZAZQH0uI3NDI1"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8964154107:AAHy0AD0pA9LwRwlmi3zDaBzq9G18xeUAYc")
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1003852203400"))

app_flask = Flask('')
@app_flask.route('/')
def home(): return f"{BRAND} Bot is Alive! 24x7 ON - Live"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

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
        return m.status in ['member','administrator','creator']
    except: return False

def fetch_with_bypass(url):
    headers = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}
    try:
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        if r.status_code == 200 and len(r.text) > 300: return r.text
    except: pass
    try:
        proxy = f"https://api.allorigins.win/raw?url={url}"
        r = requests.get(proxy, timeout=20)
        if r.status_code == 200: return r.text
    except: pass
    return "<h1>Content via Proxy</h1>"

def deep_clone_site(start_url):
    html_text = fetch_with_bypass(start_url)
    final = f"<!DOCTYPE html><html><head><meta charset='UTF-8'><base href='{start_url}'><title>{BRAND}</title></head><body><h2>{BRAND}</h2>{html_text}</body></html>"
    with open(FILE_NAME, "w", encoding="utf-8") as f: f.write(final)
    return FILE_NAME

URL_ASK_MSG = "Send a Website URL to start! Example: https://example.com"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if await check_joined(context.bot, uid):
        uid_s = str(uid)
        if uid_s not in passwords_db:
            passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
        user_state[uid] = {"joined": True, "code_verified": False}
        await update.message.reply_text(f"✅ JOIN SUCCESS! Code: `{passwords_db[uid_s]}`", parse_mode="Markdown")
    else:
        kb = [[InlineKeyboardButton("🔗 Join Channel", url=INVITE_LINK)], [InlineKeyboardButton("✅ Verify", callback_data="check_join")]]
        await update.message.reply_text(f"Join: {INVITE_LINK}", reply_markup=InlineKeyboardMarkup(kb))

async def button_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id; uid_s = str(uid)
    if await check_joined(context.bot, uid):
        if uid_s not in passwords_db:
            passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
        user_state[uid] = {"joined": True, "code_verified": False}
        await q.edit_message_text(f"✅ Code: `{passwords_db[uid_s]}`", parse_mode="Markdown")
    else: await q.answer("Join nahi kiya!", show_alert=True)

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id; uid_s = str(uid); text = update.message.text.strip()
    if not await check_joined(context.bot, uid):
        kb = [[InlineKeyboardButton("🔗 Join", url=INVITE_LINK)], [InlineKeyboardButton("✅ Verify", callback_data="check_join")]]
        await update.message.reply_text(f"Join: {INVITE_LINK}", reply_markup=InlineKeyboardMarkup(kb)); return
    if not user_state.get(uid, {}).get("code_verified", False):
        if uid_s in passwords_db and text == passwords_db[uid_s]:
            user_state[uid] = {"joined": True, "code_verified": True}
            await update.message.reply_text(URL_ASK_MSG); return
        else:
            if uid_s not in passwords_db:
                passwords_db[uid_s] = f"BODO-{random.randint(1000,9999)}"; save_db(passwords_db)
            await update.message.reply_text(f"Galat Code! Sahi: `{passwords_db[uid_s]}`", parse_mode="Markdown"); return
    url = text
    if not url.startswith("http"): url = "https://" + url
    msg = await update.message.reply_text(f"⏳ Fetching {url}")
    file_path = deep_clone_site(url)
    size_kb = os.path.getsize(file_path) / 1024
    caption = f"✅ HTML DONE! File: {FILE_NAME} Size: {size_kb:.1f} KB By: {BRAND} JOIN: {INVITE_LINK}"
    await update.message.reply_document(document=open(file_path, "rb"), filename=FILE_NAME, caption=caption)
    await msg.delete()

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    # FIX FOR Render Python 3.13 - event loop error
    try:
        asyncio.set_event_loop(asyncio.new_event_loop())
    except: pass
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_check, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    print(f"{BRAND} Running - Fixed event loop")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__': main()
