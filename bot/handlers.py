import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# ============================
# COMMAND HANDLERS
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = f"""
👋 Welcome to FileFormatProBot, {user.first_name}!

I can convert your files between different formats.

🔹 **What I can do:**
• 📸 Image conversion: JPEG, PNG, WebP, GIF, TIFF, BMP
• 📄 Document conversion: PDF, DOCX, TXT, HTML
• 🎵 Audio conversion: MP3, WAV, OGG, FLAC
• 🎬 Video conversion: MP4, MKV, AVI, WEBM
• 📦 Archive extraction: ZIP, RAR, 7Z, TAR
• 📊 Spreadsheet conversion: XLSX, CSV, ODS

📌 **How to use:**
1. Send me any file
2. Choose the format you want to convert to
3. I'll send you the converted file!

Type /help for more information.
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when /help is issued."""
    help_text = """
🆘 **Help Center**

**How to use this bot:**
1. Send me any file
2. I'll show you available conversion options
3. Click the format you want
4. Receive your converted file!

**Supported formats:**
• Images: JPEG, PNG, WebP, GIF, TIFF, BMP, ICO
• Documents: PDF, DOCX, TXT, HTML, ODT, RTF, MD
• Audio: MP3, WAV, OGG, FLAC, M4A, AAC
• Video: MP4, MKV, AVI, WEBM, MOV, FLV
• Archives: ZIP, RAR, 7Z, TAR, GZ
• Spreadsheets: XLSX, CSV, ODS

**Commands:**
/start - Show welcome message
/help - Show this help
/formats - List all supported formats
/about - About this bot

**Size Limits:**
• Max file size: 50MB
• Batch processing: Coming soon

Questions? Contact @your_support_username
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def formats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all supported formats."""
    formats_text = """
📋 **Supported Formats**

**🖼️ Images:**
JPEG, PNG, WebP, GIF, TIFF, BMP, ICO

**📄 Documents:**
PDF, DOCX, TXT, HTML, ODT, RTF, MD

**🎵 Audio:**
MP3, WAV, OGG, FLAC, M4A, AAC

**🎬 Video:**
MP4, MKV, AVI, WEBM, MOV, FLV

**📦 Archives:**
ZIP, RAR, 7Z, TAR, GZ

**📊 Spreadsheets:**
XLSX, CSV, ODS

**📚 Ebooks:**
EPUB, MOBI, PDF, TXT

**Just send a file to get started!**
"""
    await update.message.reply_text(formats_text, parse_mode='Markdown')

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot."""
    about_text = """
ℹ️ **About FileFormatProBot**

Version: 1.0.0
Created: 2026

This bot helps you convert files between different formats quickly and easily. No registration required, no limits on file size.

**Why use this bot?**
• ✅ 100% free to use
• ✅ No registration required
• ✅ Fast conversion
• ✅ 50+ supported formats
• ✅ Your privacy is respected

**Technical Details:**
• Built with Python 3.11
• Uses python-telegram-bot library
• Hosted on Railway
• All processing is done on the server

**Privacy Policy:**
We do not store your files. All files are deleted immediately after conversion.

Built with ❤️ using Python and the Telegram Bot API.
"""
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads."""
    try:
        # Check if file is in message
        file = None
        if update.message.document:
            file = update.message.document
        elif update.message.photo:
            # Get the largest photo
            file = update.message.photo[-1]
        elif update.message.video:
            file = update.message.video
        elif update.message.audio:
            file = update.message.audio
        elif update.message.voice:
            file = update.message.voice
        
        if not file:
            await update.message.reply_text("❌ Please send a valid file.")
            return
        
        # Get file info
        file_name = getattr(file, 'file_name', 'unknown_file')
        file_id = file.file_id
        
        # Get file size
        file_size = getattr(file, 'file_size', 0)
        max_size = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size:
            await update.message.reply_text(
                f"❌ File too large! Max size is 50MB. Your file is {file_size // (1024*1024)}MB."
            )
            return
        
        # Store file info in context
        context.user_data['file_id'] = file_id
        context.user_data['file_name'] = file_name
        
        # Create keyboard with conversion options
        keyboard = [
            [InlineKeyboardButton("🖼️ Image Formats", callback_data='image_formats')],
            [InlineKeyboardButton("📄 Document Formats", callback_data='doc_formats')],
            [InlineKeyboardButton("🎵 Audio Formats", callback_data='audio_formats')],
            [InlineKeyboardButton("🎬 Video Formats", callback_data='video_formats')],
            [InlineKeyboardButton("📦 Archive Formats", callback_data='archive_formats')],
            [InlineKeyboardButton("📊 Spreadsheet Formats", callback_data='spreadsheet_formats')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Get file extension
        ext = os.path.splitext(file_name)[1].lower()
        
        await update.message.reply_text(
            f"📁 **Received:** `{file_name}`\n\n"
            f"📊 **Size:** {file_size // 1024} KB\n"
            f"📂 **Type:** {ext if ext else 'Unknown'}\n\n"
            f"Choose the format you want to convert to:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await update.message.reply_text("❌ An error occurred while processing your file. Please try again.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Show format options based on category
    if data == 'image_formats':
        keyboard = [
            [InlineKeyboardButton("JPEG", callback_data='convert_jpeg'),
             InlineKeyboardButton("PNG", callback_data='convert_png')],
            [InlineKeyboardButton("WebP", callback_data='convert_webp'),
             InlineKeyboardButton("GIF", callback_data='convert_gif')],
            [InlineKeyboardButton("TIFF", callback_data='convert_tiff'),
             InlineKeyboardButton("BMP", callback_data='convert_bmp')],
            [InlineKeyboardButton("ICO", callback_data='convert_ico')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🖼️ **Choose image format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'doc_formats':
        keyboard = [
            [InlineKeyboardButton("PDF", callback_data='convert_pdf'),
             InlineKeyboardButton("DOCX", callback_data='convert_docx')],
            [InlineKeyboardButton("TXT", callback_data='convert_txt'),
             InlineKeyboardButton("HTML", callback_data='convert_html')],
            [InlineKeyboardButton("ODT", callback_data='convert_odt'),
             InlineKeyboardButton("RTF", callback_data='convert_rtf')],
            [InlineKeyboardButton("MD", callback_data='convert_md')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📄 **Choose document format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'audio_formats':
        keyboard = [
            [InlineKeyboardButton("MP3", callback_data='convert_mp3'),
             InlineKeyboardButton("WAV", callback_data='convert_wav')],
            [InlineKeyboardButton("OGG", callback_data='convert_ogg'),
             InlineKeyboardButton("FLAC", callback_data='convert_flac')],
            [InlineKeyboardButton("M4A", callback_data='convert_m4a'),
             InlineKeyboardButton("AAC", callback_data='convert_aac')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎵 **Choose audio format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'video_formats':
        keyboard = [
            [InlineKeyboardButton("MP4", callback_data='convert_mp4'),
             InlineKeyboardButton("MKV", callback_data='convert_mkv')],
            [InlineKeyboardButton("AVI", callback_data='convert_avi'),
             InlineKeyboardButton("WEBM", callback_data='convert_webm')],
            [InlineKeyboardButton("MOV", callback_data='convert_mov'),
             InlineKeyboardButton("FLV", callback_data='convert_flv')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🎬 **Choose video format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'archive_formats':
        keyboard = [
            [InlineKeyboardButton("ZIP", callback_data='convert_zip'),
             InlineKeyboardButton("RAR", callback_data='convert_rar')],
            [InlineKeyboardButton("7Z", callback_data='convert_7z'),
             InlineKeyboardButton("TAR", callback_data='convert_tar')],
            [InlineKeyboardButton("GZ", callback_data='convert_gz')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📦 **Choose archive format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'spreadsheet_formats':
        keyboard = [
            [InlineKeyboardButton("XLSX", callback_data='convert_xlsx'),
             InlineKeyboardButton("CSV", callback_data='convert_csv')],
            [InlineKeyboardButton("ODS", callback_data='convert_ods')],
            [InlineKeyboardButton("🔙 Back", callback_data='back_to_main')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📊 **Choose spreadsheet format:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data == 'back_to_main':
        keyboard = [
            [InlineKeyboardButton("🖼️ Image Formats", callback_data='image_formats')],
            [InlineKeyboardButton("📄 Document Formats", callback_data='doc_formats')],
            [InlineKeyboardButton("🎵 Audio Formats", callback_data='audio_formats')],
            [InlineKeyboardButton("🎬 Video Formats", callback_data='video_formats')],
            [InlineKeyboardButton("📦 Archive Formats", callback_data='archive_formats')],
            [InlineKeyboardButton("📊 Spreadsheet Formats", callback_data='spreadsheet_formats')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📁 **Choose the format you want to convert to:**\n\n"
            "Select a category from the buttons below.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif data.startswith('convert_'):
        # Handle actual conversion
        format_type = data.replace('convert_', '')
        
        # Get file info from context
        file_id = context.user_data.get('file_id')
        file_name = context.user_data.get('file_name', 'file')
        
        if not file_id:
            await query.edit_message_text(
                "❌ **File not found!**\n\n"
                "Please send the file again and select the conversion format.",
                parse_mode='Markdown'
            )
            return
        
        # Send processing message
        await query.edit_message_text(
            f"🔄 **Converting to {format_type.upper()}...**\n\n"
            f"📁 File: `{file_name}`\n"
            "⏳ Please wait, this may take a moment...",
            parse_mode='Markdown'
        )
        
        try:
            # Get the file from Telegram
            file_obj = await context.bot.get_file(file_id)
            
            # Download the file
            input_path = f"temp_{file_id}.tmp"
            await file_obj.download_to_drive(input_path)
            
            # Here you would implement actual conversion logic
            # For now, we'll just send a demo message
            await query.message.reply_text(
                f"✅ **Conversion Complete!**\n\n"
                f"📁 Original: `{file_name}`\n"
                f"🔄 Converted to: **{format_type.upper()}**\n"
                f"📊 Size: {os.path.getsize(input_path) // 1024} KB\n\n"
                f"*Full conversion functionality coming soon!*",
                parse_mode='Markdown'
            )
            
            # Clean up temp file
            if os.path.exists(input_path):
                os.remove(input_path)
                
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            await query.message.reply_text(
                f"❌ **Conversion failed**\n\n"
                f"Error: {str(e)}\n\n"
                "Please try again or contact support."
            )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text(
        "❌ Unknown command. Please use /start or /help to see available commands."
    )
