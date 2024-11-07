# app/converter.py
import os
import subprocess
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DocumentConverter:
    def __init__(self):
        self.wine_prefix = "/opt/wineprefix"
        self.convert_script = "/opt/wineprefix/drive_c/app/convert_script.py"
        self._create_conversion_script()

    def _create_conversion_script(self):
        """Create the Windows Python conversion script."""
        script_content = '''
import os
import sys
import pythoncom
import win32com.client

def convert_to_pdf(input_file, output_file):
    print(f"Starting conversion: {input_file} -> {output_file}")
    
    # Initialize COM
    pythoncom.CoInitialize()
    word = None
    
    try:
        # Create Word application
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        # Convert paths to Windows format (assuming they're in C: drive)
        input_path = os.path.abspath(input_file)
        output_path = os.path.abspath(output_file)
        
        print(f"Opening document: {input_path}")
        doc = word.Documents.Open(input_path)
        print("Document opened successfully")
        
        print(f"Saving as PDF: {output_path}")
        doc.SaveAs(output_path, FileFormat=17)  # wdFormatPDF = 17
        print("PDF saved successfully")
        
        doc.Close()
        print("Document closed")
        return True
        
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return False
        
    finally:
        if word:
            try:
                word.Quit()
            except:
                pass
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: script.py input_file output_file")
        sys.exit(1)
    
    success = convert_to_pdf(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
'''
        try:
            # Ensure directory exists
            script_dir = os.path.dirname(self.convert_script)
            os.makedirs(script_dir, exist_ok=True)
            
            with open(self.convert_script, 'w') as f:
                f.write(script_content)
            logger.info(f"Created conversion script at {self.convert_script}")
        except Exception as e:
            logger.error(f"Failed to create conversion script: {str(e)}")
            raise

    def _convert_to_windows_path(self, path: str) -> str:
        """Convert Linux path to Windows path."""
        # Remove /opt/wineprefix/drive_c and replace with C:
        if path.startswith('/opt/wineprefix/drive_c/'):
            return 'C:' + path[len('/opt/wineprefix/drive_c'):].replace('/', '\\')
        return path

    def convert_to_pdf(self, input_file: str, output_file: str) -> Optional[str]:
        """Convert a document to PDF using Wine's Python and Word."""
        logger.info(f"Starting conversion of {input_file} to {output_file}")
        
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return None

        try:
            # Convert paths to Windows format
            win_input = self._convert_to_windows_path(input_file)
            win_output = self._convert_to_windows_path(output_file)
            
            logger.info(f"Windows paths - Input: {win_input}, Output: {win_output}")
            
            # Prepare command
            command = [
                'xvfb-run',
                '-a',
                'wine',
                'python',
                'C:\\app\\convert_script.py',  # Use Windows path format
                win_input,
                win_output
            ]
            
            logger.info(f"Executing command: {' '.join(command)}")
            
            # Set environment variables
            env = os.environ.copy()
            env['WINEPREFIX'] = self.wine_prefix
            env['WINEDEBUG'] = '-all'
            
            # Run conversion
            process = subprocess.run(
                command,
                env=env,
                capture_output=True,
                text=True,
                check=False
            )

            # Log output
            if process.stdout:
                logger.info(f"Conversion output:\n{process.stdout}")
            if process.stderr:
                logger.error(f"Conversion errors:\n{process.stderr}")

            # Check result
            if process.returncode == 0 and os.path.exists(output_file):
                logger.info(f"Successfully converted to PDF. Size: {os.path.getsize(output_file)} bytes")
                return output_file
            
            logger.error(f"Conversion failed with return code {process.returncode}")
            return None

        except Exception as e:
            logger.error(f"Error during conversion: {str(e)}", exc_info=True)
            return None