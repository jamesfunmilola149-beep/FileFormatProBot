import os
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Get bot token
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Create a simple bot instance (only if token exists)
application = None
if BOT_TOKEN:
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ Bot application created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create bot: {e}")

# ============================
# SIMPLE HANDLERS
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message."""
    user = update.effective_user
    welcome_text = f"""
👋 Welcome to FileFormatProBot, {user.first_name}!

I convert files between different formats.

📌 How to use:
1. Send me any file
2. Choose the format you want
3. I'll convert it for you!

Supported: Images, Documents, Audio, Video, Archives
"""
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message."""
    help_text = """
🆘 Help

Send me a file and I'll show you conversion options.

Commands:
/start - Welcome
/help - This help
/formats - Supported formats
/about - About this bot
"""
    await update.message.reply_text(help_text)

async def formats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List supported formats."""
    formats_text = """
📋 Supported Formats

🖼️ Images: JPEG, PNG, WebP, GIF, TIFF, BMP
📄 Documents: PDF, DOCX, TXT, HTML, ODT
🎵 Audio: MP3, WAV, OGG, FLAC, M4A
🎬 Video: MP4, MKV, AVI, WEBM, MOV
📦 Archives: ZIP, RAR, 7Z, TAR, GZ
📊 Spreadsheets: XLSX, CSV, ODS
"""
    await update.message.reply_text(formats_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot."""
    about_text = """
ℹ️ FileFormatProBot v1.0

Free file converter for Telegram.
50+ formats supported.
No registration required.

Built with Python & ❤️
"""
    await update.message.reply_text(about_text)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads."""
    file = update.message.document or update.message.photo or update.message.video or update.message.audio
    
    if not file:
        await update.message.reply_text("❌ Please send a valid file.")
        return
    
    file_name = getattr(file, 'file_name', 'file')
    context.user_data['file_id'] = file.file_id
    
    # Simple keyboard
    keyboard = [
        [InlineKeyboardButton("🖼️ Image", callback_data='image'),
         InlineKeyboardButton("📄 Document", callback_data='document')],
        [InlineKeyboardButton("🎵 Audio", callback_data='audio'),
         InlineKeyboardButton("🎬 Video", callback_data='video')],
        [InlineKeyboardButton("📦 Archive", callback_data='archive')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📁 Received: {file_name}\n\nChoose conversion type:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    await query.edit_message_text(
        f"✅ You selected: {data}\n\n"
        f"🔄 Conversion feature coming soon!\n"
        f"The bot will convert your file shortly."
    )

# Register handlers
if application:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("formats", formats_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, handle_file))
    application.add_handler(CallbackQueryHandler(button_callback))
    logger.info("✅ Handlers registered")

# ============================
# FLASK ROUTES - CRITICAL FOR RAILWAY
# ============================

@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        "status": "online",
        "bot": "FileFormatProBot",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    """Health check - MUST return 200 OK quickly."""
    return "OK", 200

@app.route('/ping')
def ping():
    """Simple ping for healthchecks."""
    return "pong", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint."""
    if not application:
        return jsonify({"ok": False, "error": "Bot not initialized"}), 500
    
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"ok": False}), 400
        
        # Process update asynchronously
        import asyncio
        update = Update.de_json(update_data, application.bot)
        asyncio.create_task(application.process_update(update))
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"ok": False}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook URL."""
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
    logger.info(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
