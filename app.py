import os
import logging
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================
# CRITICAL: HEALTHCHECK MUST WORK
# ============================

@app.route('/')
def index():
    """Root endpoint - must respond quickly."""
    return "OK", 200

@app.route('/health')
def health():
    """Health check - MUST return 200 OK in under 1 second."""
    return "OK", 200

@app.route('/ping')
def ping():
    """Ping endpoint."""
    return "pong", 200

@app.route('/status')
def status():
    """Status endpoint."""
    return jsonify({
        "status": "online",
        "bot": "FileFormatProBot",
        "version": "1.0.0",
        "timestamp": "2026"
    })

# ============================
# TELEGRAM BOT HANDLERS
# ============================

# Import telegram modules here - so Flask starts first
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    from dotenv import load_dotenv
    
    load_dotenv()
    
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    application = None
    
    if BOT_TOKEN:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Bot initialized")
        
        # ============================
        # BOT HANDLERS
        # ============================
        
        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            await update.message.reply_text(
                f"👋 Welcome {user.first_name}!\n\n"
                f"I'm FileFormatProBot - your file converter.\n\n"
                f"📌 Send me any file to get started!"
            )
        
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "🆘 Help\n\n"
                "Send me a file and I'll convert it!\n"
                "Commands: /start, /help, /about"
            )
        
        async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "ℹ️ FileFormatProBot v1.0\n"
                "Convert files between formats.\n"
                "Built with Python ❤️"
            )
        
        async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
            file = update.message.document or update.message.photo or update.message.video or update.message.audio
            
            if not file:
                await update.message.reply_text("❌ Please send a valid file.")
                return
            
            file_name = getattr(file, 'file_name', 'file')
            context.user_data['file_id'] = file.file_id
            
            keyboard = [
                [InlineKeyboardButton("🖼️ Image", callback_data='image')],
                [InlineKeyboardButton("📄 Document", callback_data='document')],
                [InlineKeyboardButton("🎵 Audio", callback_data='audio')],
                [InlineKeyboardButton("🎬 Video", callback_data='video')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"📁 Received: {file_name}\n\nChoose conversion type:",
                reply_markup=reply_markup
            )
        
        async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                f"✅ Converting to {query.data}...\n\n"
                f"Feature coming soon!"
            )
        
        # Register handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        logger.info("✅ Bot handlers registered")
        
except ImportError as e:
    logger.warning(f"Telegram imports failed: {e}")
    application = None

# ============================
# WEBHOOK ENDPOINT
# ============================

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook."""
    if not application:
        return jsonify({"ok": False, "error": "Bot not initialized"}), 500
    
    try:
        import asyncio
        update_data = request.get_json()
        if not update_data:
            return jsonify({"ok": False}), 400
        
        update = Update.de_json(update_data, application.bot)
        asyncio.create_task(application.process_update(update))
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"ok": False}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook."""
    if not application:
        return jsonify({"error": "Bot not initialized"}), 500
    
    webhook_url = os.environ.get("WEBHOOK_URL", "")
    if not webhook_url:
        return jsonify({"error": "WEBHOOK_URL not set"}), 500
    
    try:
        response = application.bot.set_webhook(webhook_url)
        return jsonify({"ok": response, "url": webhook_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# RUN APPLICATION
# ============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
