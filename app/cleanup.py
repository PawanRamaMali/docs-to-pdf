# app/cleanup.py
import os
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def cleanup_old_files(directory: str, max_age_minutes: int = 30):
    """Clean up files older than max_age_minutes in the specified directory."""
    try:
        current_time = time.time()
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return
            
        for file_path in directory_path.glob('*'):
            if file_path.is_file():
                file_age_minutes = (current_time - file_path.stat().st_mtime) / 60
                if file_age_minutes > max_age_minutes:
                    try:
                        file_path.unlink()
                        logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting file {file_path}: {str(e)}")
                        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

# You can run this periodically using a scheduler if needed