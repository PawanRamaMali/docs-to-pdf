import os
import logging
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uuid
import subprocess
from app.converter import DocumentConverter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document to PDF Converter")

# Initialize the converter
converter = DocumentConverter()

# Constants
UPLOAD_DIR = "/opt/wineprefix/drive_c/uploads"
ALLOWED_EXTENSIONS = {'.docx', '.doc', '.rtf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/test-environment")
async def test_environment():
    """Test Wine and Office environment"""
    try:
        # Test Wine
        wine_ver = subprocess.run(
            ['wine', '--version'], 
            capture_output=True, 
            text=True
        )
        
        # Test Python in Wine
        wine_python = subprocess.run(
            ['wine', 'python', '--version'],
            capture_output=True,
            text=True
        )
        
        # Test for Office components
        test_script = '''
import win32com.client
word = win32com.client.Dispatch("Word.Application")
word.Quit()
'''
        with open('/tmp/test.py', 'w') as f:
            f.write(test_script)
            
        office_test = subprocess.run(
            ['wine', 'python', '/tmp/test.py'],
            capture_output=True,
            text=True
        )
        
        return JSONResponse({
            "wine_version": wine_ver.stdout if wine_ver.returncode == 0 else "Failed",
            "wine_python": wine_python.stdout if wine_python.returncode == 0 else "Failed",
            "office_test": "Success" if office_test.returncode == 0 else f"Failed: {office_test.stderr}"
        })
        
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)

@app.get("/detailed-test")
async def detailed_test():
    """Run detailed environment test"""
    try:
        result = subprocess.run(
            ['wine', 'python', '/opt/wineprefix/drive_c/app/test_env.py'],
            capture_output=True,
            text=True
        )
        return JSONResponse({
            "output": result.stdout,
            "errors": result.stderr,
            "return_code": result.returncode
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e)
        }, status_code=500)
        
@app.post("/convert/")
async def convert_document(file: UploadFile):
    """Convert uploaded document to PDF"""
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create unique filenames
    unique_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{unique_id}{file_ext}")
    output_path = os.path.join(UPLOAD_DIR, f"{unique_id}.pdf")
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Convert to PDF
        result = converter.convert_to_pdf(input_path, output_path)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Conversion failed"
            )
        
        # Return the PDF file
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"{os.path.splitext(file.filename)[0]}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        
    finally:
        # Cleanup temporary files
        for path in [input_path, output_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Error cleaning up file {path}: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}