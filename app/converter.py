# converter.py
import os
import pythoncom
import win32com.client
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DocumentConverter:
    def __init__(self):
        self.wdFormatPDF = 17
        
    def convert_to_pdf(self, input_file: str, output_file: str) -> Optional[str]:
        """
        Convert a document to PDF using Word automation.
        
        Args:
            input_file: Path to input document (.docx, .doc, or .rtf)
            output_file: Path to output PDF
            
        Returns:
            Optional[str]: Path to output PDF if successful, None otherwise
        """
        try:
            # Ensure input file exists
            if not os.path.isfile(input_file):
                logger.error(f"Input file not found: {input_file}")
                return None
                
            # Check file extension
            if not input_file.lower().endswith(('.docx', '.doc', '.rtf')):
                logger.error("Input file must be a .docx, .doc or .rtf file")
                return None
                
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file) or "."
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize COM
            pythoncom.CoInitialize()
            
            # Create Word application
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            try:
                # Convert paths to absolute Windows paths
                abs_input = os.path.abspath(input_file)
                abs_output = os.path.abspath(output_file)
                
                # Open and convert document
                doc = word.Documents.Open(abs_input)
                doc.SaveAs(abs_output, FileFormat=self.wdFormatPDF)
                doc.Close()
                
                logger.info(f"Successfully converted {input_file} to PDF")
                return output_file
                
            except Exception as e:
                logger.error(f"Error during conversion: {str(e)}")
                return None
                
            finally:
                # Clean up Word
                try:
                    word.Quit()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in conversion process: {str(e)}")
            return None
            
        finally:
            # Clean up COM
            try:
                pythoncom.CoUninitialize()
            except:
                pass