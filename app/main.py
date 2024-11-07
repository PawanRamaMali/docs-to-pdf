# app/main.py
import os
import logging
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
from app.converter import DocumentConverter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document to PDF Converter")

# Initialize the converter
converter = DocumentConverter()

# Constants
UPLOAD_DIR = "/opt/wineprefix/drive_c/uploads"
ALLOWED_EXTENSIONS = {'.docx', '.doc', '.rtf'}

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def cleanup_files(input_path: str, output_path: str):
    """Background task to cleanup temporary files after response is sent."""
    try:
        if input_path and os.path.exists(input_path):
            os.remove(input_path)
            logger.info(f"Cleaned up input file: {input_path}")
            
        if output_path and os.path.exists(output_path):
            os.remove(output_path)
            logger.info(f"Cleaned up output file: {output_path}")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

@app.post("/convert/")
async def convert_document(file: UploadFile, background_tasks: BackgroundTasks):
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
    
    logger.info(f"Processing file: {file.filename}")
    logger.info(f"Input path: {input_path}")
    logger.info(f"Output path: {output_path}")
    
    try:
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        logger.info(f"Saved input file, size: {os.path.getsize(input_path)} bytes")
        
        # Convert to PDF
        result = converter.convert_to_pdf(input_path, output_path)
        
        if not result or not os.path.exists(output_path):
            if os.path.exists(input_path):
                os.remove(input_path)
            raise HTTPException(
                status_code=500,
                detail="Conversion failed"
            )
        
        # Schedule cleanup to run after response is sent
        background_tasks.add_task(cleanup_files, input_path, output_path)
        
        # Return the PDF file
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"{os.path.splitext(file.filename)[0]}.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}", exc_info=True)
        # Clean up in case of error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}