import os
import subprocess
from typing import Optional

class DocumentConverter:
    def __init__(self):
        self.wine_python = "wine python"

    def convert_to_pdf(self, input_file: str, output_file: str) -> Optional[str]:
        """
        Convert a document to PDF format using a separate Wine Python process.
        """
        # Create the conversion script
        script_path = os.path.join(os.path.dirname(__file__), "convert_script.py")
        with open(script_path, "w") as f:
            f.write("""
import os
import pythoncom
import win32com.client

def convert(input_file, output_file):
    wdFormatPDF = 17
    pythoncom.CoInitialize()
    
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        
        doc = word.Documents.Open(os.path.abspath(input_file))
        doc.SaveAs(os.path.abspath(output_file), FileFormat=wdFormatPDF)
        doc.Close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
        
    finally:
        word.Quit()
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    import sys
    success = convert(sys.argv[1], sys.argv[2])
    sys.exit(0 if success else 1)
""")

        try:
            # Run the conversion script using Wine Python
            process = subprocess.run(
                f"{self.wine_python} {script_path} {input_file} {output_file}",
                shell=True,
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0 and os.path.exists(output_file):
                return output_file
                
            print(f"Conversion failed: {process.stderr}")
            return None
            
        except Exception as e:
            print(f"Error during conversion: {e}")
            return None