import shutil
import pythoncom
import win32com.client
import json

def convert_to_pdf(input_file: str, output_file: str) -> str:
    """Convert a .docx or .rtf file to PDF.

    Parameters:
    - input_file (str): Path to the .docx or .rtf file.
    - output_file (str): Path where the output PDF should be saved.
    
    Returns:
    - str: JSON response indicating success or error.
    """
    response = {"errcode": 0, "errmsg": ""}
    
    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch("Word.Application")
        doc = word.Documents.Open(input_file)
        doc.SaveAs(output_file, FileFormat=17)  # 17 is the PDF format
        doc.Close()
        word.Quit()
    except Exception as e:
        response["errcode"] = 1
        response["errmsg"] = str(e)
    finally:
        pythoncom.CoUninitialize()
    
    return json.dumps(response)

# Example usage:
# print(convert_to_pdf("path/to/input.docx", "path/to/output.pdf"))
