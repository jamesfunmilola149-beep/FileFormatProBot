from flask import Flask, request, jsonify
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# ============================
# HEALTHCHECK ENDPOINTS - MUST WORK
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
# TELEGRAM BOT (Lazy Load)
# ============================

def get_bot():
    """Lazy load bot to avoid startup delays."""
    global bot_instance
    if 'bot_instance' not in globals():
        try:
            from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
            from dotenv import load_dotenv
            
            load_dotenv()
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            
            if not token:
                logger.error("❌ No TELEGRAM_BOT_TOKEN found")
                return None
            
            app_instance = Application.builder().token(token).build()
            
            # Simple handlers
            async def start(update, context):
                await update.message.reply_text(
                    "👋 Welcome to FileFormatProBot!\n\n"
                    "Send me a file and I'll convert it!"
                )
            
            async def help_cmd(update, context):
                await update.message.reply_text(
                    "Send me a file to convert.\n"
                    "Commands: /start, /help, /about"
                )
            
            async def about(update, context):
                await update.message.reply_text(
                    "FileFormatProBot v1.0\n"
                    "File converter for Telegram"
                )
            
            async def handle_file(update, context):
                file = update.message.document or update.message.photo or update.message.video or update.message.audio
                if not file:
                    await update.message.reply_text("Please send a valid file.")
                    return
                
                keyboard = [
                    [InlineKeyboardButton("🖼️ Image", callback_data='image')],
                    [InlineKeyboardButton("📄 Document", callback_data='doc')],
                    [InlineKeyboardButton("🎵 Audio", callback_data='audio')],
                    [InlineKeyboardButton("🎬 Video", callback_data='video')],
                ]
                await update.message.reply_text(
                    f"📁 Received: {getattr(file, 'file_name', 'file')}\n\nChoose format:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            
            async def button_callback(update, context):
                query = update.callback_query
                await query.answer()
                await query.edit_message_text(f"✅ Converting to {query.data}...")
            
            # Register handlers
            app_instance.add_handler(CommandHandler("start", start))
            app_instance.add_handler(CommandHandler("help", help_cmd))
            app_instance.add_handler(CommandHandler("about", about))
            app_instance.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
            app_instance.add_handler(CallbackQueryHandler(button_callback))
            
            logger.info("✅ Bot initialized successfully")
            bot_instance = app_instance
            return bot_instance
        except Exception as e:
            logger.error(f"❌ Bot initialization failed: {e}")
            return None
    return bot_instance

# ============================
# WEBHOOK ENDPOINT
# ============================

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        bot = get_bot()
        if not bot:
            return jsonify({"ok": False, "error": "Bot not ready"}), 500
        
        import asyncio
        from telegram import Update
        
        data = request.get_json()
        if not data:
            return jsonify({"ok": False}), 400
        
        update = Update.de_json(data, bot.bot)
        asyncio.create_task(bot.process_update(update))
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"ok": False}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot = get_bot()
    if not bot:
        return jsonify({"error": "Bot not ready"}), 500
    
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if not webhook_url:
        return jsonify({"error": "WEBHOOK_URL not set"}), 500
    
    try:
        result = bot.bot.set_webhook(webhook_url)
        return jsonify({"ok": result, "url": webhook_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# RUN APP
# ============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
