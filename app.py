import os
import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv

# Import bot modules
from bot.handlers import start, help_command, formats, about, handle_file, button_callback, unknown_command

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
if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
    # Don't raise error, let it run for healthcheck
    BOT_TOKEN = "dummy_token_for_healthcheck"

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

# Create Telegram application (only if token is valid)
application = None
if BOT_TOKEN and BOT_TOKEN != "dummy_token_for_healthcheck":
    application = Application.builder().token(BOT_TOKEN).build()
    setup_handlers()

def setup_handlers():
    """Setup all bot handlers."""
    if not application:
        return
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("formats", formats))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO | filters.VIDEO | filters.AUDIO, 
        handle_file
    ))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

# ============================
# FLASK ROUTES
# ============================

@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        "status": "online",
        "bot": "FileFormatProBot",
        "version": "1.0.0",
        "message": "Bot is running!"
    })

@app.route('/health')
def health():
    """Health check for Railway - MUST return 200 quickly."""
    return jsonify({"status": "healthy", "uptime": "running"}), 200

@app.route('/ping')
def ping():
    """Simple ping endpoint for healthchecks."""
    return "pong", 200

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming webhook updates."""
    if not application:
        return jsonify({"ok": False, "error": "Bot not initialized"}), 500
    try:
        update_data = request.get_json()
        if not update_data:
            return jsonify({"ok": False, "error": "No data provided"}), 400
        
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Set webhook URL."""
    if not application:
        return jsonify({"ok": False, "error": "Bot not initialized"}), 500
    try:
        webhook_url = WEBHOOK_URL
        if not webhook_url:
            return jsonify({"ok": False, "error": "WEBHOOK_URL not set"}), 500
        response = application.bot.set_webhook(webhook_url)
        if response:
            return jsonify({"ok": True, "message": f"Webhook set to {webhook_url}"})
        else:
            return jsonify({"ok": False, "error": "Failed to set webhook"}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

# ============================
# RUN APPLICATION
# ============================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    
    # In development mode, use polling
    if os.environ.get("FLASK_ENV") == "development":
        logger.info("🚀 Starting bot in development mode...")
        if application:
            application.run_polling()
        else:
            app.run(host="0.0.0.0", port=port)
    else:
        # In production, use webhook via Flask
        logger.info("🚀 Starting Flask server for webhook on port %s...", port)
        app.run(host="0.0.0.0", port=port)
