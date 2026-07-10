import os
import sys
import threading
import asyncio
from flask import Flask, request, jsonify

# Create Flask app
app = Flask(__name__)

# ============================
# FLASK ROUTES (FOR RAILWAY)
# ============================

@app.route('/')
def index():
    return "FileFormatProBot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/status')
def status():
    return jsonify({"status": "running", "bot": "FileFormatProBot"})

# ============================
# TELEGRAM BOT (POLLING MODE)
# ============================

def run_bot():
    """Run Telegram bot in a separate thread using polling."""
    try:
        import asyncio
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from telegram import Update
        
        # Get token from environment
        TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
        
        if not TOKEN:
            print("❌ No TELEGRAM_BOT_TOKEN found!", file=sys.stderr)
            return
        
        print(f"✅ Token found: {TOKEN[:10]}...", file=sys.stderr)
        
        # Create application
        bot_app = Application.builder().token(TOKEN).build()
        
        # ============================
        # HANDLERS
        # ============================
        
        async def start(update: Update, context):
            user = update.effective_user
            await update.message.reply_text(
                f"👋 Welcome to FileFormatProBot, {user.first_name}!\n\n"
                f"📌 Send me any file and I'll convert it!\n"
                f"Commands: /start, /help, /about"
            )
        
        async def help_command(update: Update, context):
            await update.message.reply_text(
                "🆘 Help\n\n"
                "1. Send me a file\n"
                "2. I'll convert it for you!\n\n"
                "Commands: /start, /help, /about"
            )
        
        async def about_command(update: Update, context):
            await update.message.reply_text(
                "ℹ️ FileFormatProBot v1.0\n"
                "File converter for Telegram\n"
                "Built with Python ❤️"
            )
        
        async def handle_file(update: Update, context):
            file = update.message.document or update.message.photo or update.message.video or update.message.audio
            
            if not file:
                await update.message.reply_text("❌ Please send a valid file.")
                return
            
            file_name = getattr(file, 'file_name', 'file')
            await update.message.reply_text(
                f"📁 Received: {file_name}\n\n"
                f"✅ File received! I'll convert it for you."
            )
        
        async def echo(update: Update, context):
            """Echo any message (for testing)."""
            await update.message.reply_text(f"📩 You said: {update.message.text}")
        
        # ============================
        # REGISTER HANDLERS
        # ============================
        
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(CommandHandler("about", about_command))
        bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
        
        print("✅ Bot handlers registered!", file=sys.stderr)
        print("🚀 Starting bot polling...", file=sys.stderr)
        
        # Start polling
        bot_app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Bot error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

# ============================
# START BOT IN BACKGROUND
# ============================

# Start bot thread
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()
print("✅ Bot thread started!", file=sys.stderr)

# ============================
# RUN FLASK
# ============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Flask running on port {port}", file=sys.stderr)
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
