from flask import Flask, request, jsonify
import os
import sys

# Create Flask app
app = Flask(__name__)

# Print to log so we can see it's running
print("🚀 Starting Flask app...", file=sys.stderr)

@app.route('/')
def index():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "bot": "FileFormatProBot"
    })

# ============================
# TELEGRAM BOT - ONLY IF TOKEN EXISTS
# ============================

try:
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    print(f"🔑 Token found: {bool(BOT_TOKEN)}", file=sys.stderr)
    
    if BOT_TOKEN and BOT_TOKEN != "your_bot_token_here":
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        bot_app = Application.builder().token(BOT_TOKEN).build()
        
        # Simple handlers
        async def start(update, context):
            await update.message.reply_text(
                "👋 Welcome to FileFormatProBot!\n\n"
                "Send me any file to convert it!"
            )
        
        async def help_cmd(update, context):
            await update.message.reply_text(
                "Send me a file and I'll convert it!\n"
                "Commands: /start, /help"
            )
        
        async def handle_file(update, context):
            file = update.message.document
            if file:
                await update.message.reply_text(
                    f"📁 Received: {file.file_name}\n\n"
                    f"✅ File received! Conversion coming soon."
                )
            else:
                await update.message.reply_text("Please send a file.")
        
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_cmd))
        bot_app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        
        print("✅ Bot initialized successfully", file=sys.stderr)
    else:
        print("⚠️ No valid token found", file=sys.stderr)
        bot_app = None
        
except Exception as e:
    print(f"❌ Bot error: {e}", file=sys.stderr)
    bot_app = None

# ============================
# WEBHOOK ENDPOINT
# ============================

@app.route('/webhook', methods=['POST'])
def webhook():
    if not bot_app:
        return jsonify({"ok": False, "error": "Bot not ready"}), 500
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"ok": False}), 400
        
        # Process update asynchronously
        import asyncio
        update = Update.de_json(data, bot_app.bot)
        asyncio.create_task(bot_app.process_update(update))
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        print(f"Webhook error: {e}", file=sys.stderr)
        return jsonify({"ok": False}), 500

@app.route('/set_webhook')
def set_webhook():
    if not bot_app:
        return jsonify({"error": "Bot not ready"}), 500
    
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if not webhook_url:
        return jsonify({"error": "WEBHOOK_URL not set"}), 500
    
    try:
        result = bot_app.bot.set_webhook(webhook_url)
        return jsonify({"ok": result, "url": webhook_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# RUN THE APP
# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Running on port {port}", file=sys.stderr)
    app.run(host="0.0.0.0", port=port, debug=False)
