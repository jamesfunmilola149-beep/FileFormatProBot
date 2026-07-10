import os
import sys
from flask import Flask, request, jsonify

print("🚀 Starting app...", file=sys.stderr)

app = Flask(__name__)

@app.route('/')
def index():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/status')
def status():
    return jsonify({"status": "running", "bot": "FileFormatProBot"})

# Try to initialize bot
try:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if BOT_TOKEN:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        bot_app = Application.builder().token(BOT_TOKEN).build()
        
        async def start(update, context):
            await update.message.reply_text("👋 Welcome to FileFormatProBot! Send me a file.")
        
        async def help_cmd(update, context):
            await update.message.reply_text("Send me a file to convert!")
        
        async def handle_file(update, context):
            file = update.message.document
            if file:
                await update.message.reply_text(f"📁 Received: {file.file_name}")
            else:
                await update.message.reply_text("Please send a file.")
        
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_cmd))
        bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        
        print("✅ Bot ready", file=sys.stderr)
    else:
        bot_app = None
        print("⚠️ No token", file=sys.stderr)
except Exception as e:
    print(f"❌ Bot error: {e}", file=sys.stderr)
    bot_app = None

@app.route('/webhook', methods=['POST'])
def webhook():
    if not bot_app:
        return jsonify({"ok": False}), 500
    try:
        data = request.get_json()
        if data:
            import asyncio
            update = Update.de_json(data, bot_app.bot)
            asyncio.create_task(bot_app.process_update(update))
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Running on port {port}", file=sys.stderr)
    app.run(host="0.0.0.0", port=port, debug=False)
