from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# ============================
# HEALTH CHECK - MUST WORK
# ============================

@app.route('/')
def index():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/ping')
def ping():
    return "pong", 200

# ============================
# TELEGRAM BOT - SIMPLE IMPORTS
# ============================

try:
    import telegram
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
    
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if BOT_TOKEN:
        app_bot = Application.builder().token(BOT_TOKEN).build()
        
        # Simple handlers
        async def start(update, context):
            await update.message.reply_text(
                "👋 Welcome to FileFormatProBot!\n\n"
                "Send me a file to convert it!"
            )
        
        async def help_cmd(update, context):
            await update.message.reply_text(
                "Send me a file and I'll convert it!\n"
                "Commands: /start, /help, /about"
            )
        
        async def about(update, context):
            await update.message.reply_text(
                "FileFormatProBot v1.0\n"
                "Your file converter bot"
            )
        
        async def handle_file(update, context):
            file = update.message.document
            if not file:
                await update.message.reply_text("Please send a file.")
                return
            
            keyboard = [
                [InlineKeyboardButton("📄 PDF", callback_data='pdf')],
                [InlineKeyboardButton("🖼️ PNG", callback_data='png')],
                [InlineKeyboardButton("🎵 MP3", callback_data='mp3')],
            ]
            await update.message.reply_text(
                f"Received: {file.file_name}\nChoose format:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        async def button(update, context):
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(f"Converting to {query.data}...")
        
        # Register
        app_bot.add_handler(CommandHandler("start", start))
        app_bot.add_handler(CommandHandler("help", help_cmd))
        app_bot.add_handler(CommandHandler("about", about))
        app_bot.add_handler(MessageHandler(filters.Document.ALL, handle_file))
        app_bot.add_handler(CallbackQueryHandler(button))
        
        print("✅ Bot initialized")
    else:
        app_bot = None
        print("⚠️ No token found")
        
except Exception as e:
    print(f"❌ Bot error: {e}")
    app_bot = None

# ============================
# WEBHOOK
# ============================

@app.route('/webhook', methods=['POST'])
def webhook():
    if not app_bot:
        return jsonify({"ok": False}), 500
    
    try:
        import asyncio
        data = request.get_json()
        if not data:
            return jsonify({"ok": False}), 400
        
        update = Update.de_json(data, app_bot.bot)
        asyncio.create_task(app_bot.process_update(update))
        return jsonify({"ok": True}), 200
    except Exception as e:
        return jsonify({"ok": False}), 500

# ============================
# RUN
# ============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
