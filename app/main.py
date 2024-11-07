import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
from .converter import DocumentConverter

app = FastAPI(title="Document to PDF Converter")

# Initialize the converter
converter = DocumentConverter()

# Constants
UPLOAD_DIR = "/opt/wineprefix/drive_c/uploads"
ALLOWED_EXTENSIONS = {'.docx', '.doc', '.rtf'}

@app.post("/convert/")
async def convert_document(file: UploadFile):
    """
    Convert uploaded document to PDF
    """
    try:
        # Check file extension
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

        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Convert to PDF
        result = converter.convert_to_pdf(input_path, output_path)
        
        if not result:
            raise HTTPException(status_code=500, detail="Conversion failed")

        # Return the PDF file
        return FileResponse(
            output_path,
            media_type="application/pdf",
            filename=f"{os.path.splitext(file.filename)[0]}.pdf"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temporary files
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass

@app.get("/health")
async def health_check():
    return {"status": "healthy"}