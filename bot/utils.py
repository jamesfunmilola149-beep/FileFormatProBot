import os
import logging
import magic
from PIL import Image
import PyPDF2
import docx
import pandas as pd
from pydub import AudioSegment

logger = logging.getLogger(__name__)

# ============================
# FILE TYPE DETECTION
# ============================

def get_file_type(file_path):
    """Detect file type using magic numbers."""
    try:
        mime = magic.from_file(file_path, mime=True)
        return mime
    except Exception as e:
        logger.error(f"Error detecting file type: {e}")
        return None

def get_file_extension(filename):
    """Get file extension."""
    return os.path.splitext(filename)[1].lower()

def is_image_file(filename):
    """Check if file is an image."""
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.ico']
    return get_file_extension(filename) in extensions

def is_document_file(filename):
    """Check if file is a document."""
    extensions = ['.pdf', '.docx', '.txt', '.html', '.odt', '.rtf', '.md']
    return get_file_extension(filename) in extensions

def is_audio_file(filename):
    """Check if file is audio."""
    extensions = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
    return get_file_extension(filename) in extensions

def is_video_file(filename):
    """Check if file is video."""
    extensions = ['.mp4', '.mkv', '.avi', '.webm', '.mov', '.flv']
    return get_file_extension(filename) in extensions

def is_archive_file(filename):
    """Check if file is an archive."""
    extensions = ['.zip', '.rar', '.7z', '.tar', '.gz']
    return get_file_extension(filename) in extensions

def is_spreadsheet_file(filename):
    """Check if file is a spreadsheet."""
    extensions = ['.xlsx', '.csv', '.ods']
    return get_file_extension(filename) in extensions

# ============================
# FILE SIZE UTILITIES
# ============================

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

# ============================
# IMAGE PROCESSING
# ============================

def convert_image(input_path, output_format):
    """Convert image to specified format."""
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if needed
            if output_format.lower() in ['jpg', 'jpeg'] and img.mode == 'RGBA':
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3])
                img = rgb_img
            
            output_path = f"{os.path.splitext(input_path)[0]}.{output_format.lower()}"
            img.save(output_path, format=output_format.upper())
        return output_path
    except Exception as e:
        logger.error(f"Image conversion error: {e}")
        return None

def resize_image(input_path, max_size):
    """Resize image to max dimensions."""
    try:
        with Image.open(input_path) as img:
            img.thumbnail(max_size)
            output_path = f"{os.path.splitext
