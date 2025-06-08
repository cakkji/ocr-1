from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import io
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import logging
import re
import traceback

app = FastAPI(
    title="Certificate OCR API",
    description="API for extracting information from certificates using deep learning OCR",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    reader = easyocr.Reader(['en', 'th'], gpu=True)
    device_info = reader.device if isinstance(reader.device, str) else getattr(reader.device, 'type', str(reader.device))
    logger.info(f"EasyOCR initialized successfully (device: {device_info})")
    if device_info == 'cpu':
        logger.warning("Neither CUDA nor MPS are available - defaulting to CPU. Note: This module is much faster with a GPU.")
except Exception as e:
    logger.error(f"Failed to initialize EasyOCR: {str(e)}")
    raise

def preprocess_image(image: Image.Image, save_path: str = None, upscale: int = 2, contrast: float = 1.2, threshold: int = 160, sharpen: bool = False) -> Image.Image:
    """
    Preprocess image for OCR:
    - Convert to grayscale
    - Optionally upscale
    - Adjust contrast
    - Apply threshold
    - Optionally sharpen
    """
    image = image.convert('L')
    if upscale > 1:
        image = image.resize((image.width * upscale, image.height * upscale), Image.LANCZOS)
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)
    image = image.point(lambda x: 0 if x < threshold else 255)
    if sharpen:
        image = image.filter(ImageFilter.SHARPEN)
    if save_path:
        image.save(save_path)
    return image

def fix_common_ocr_errors(text):
    # Replace common Thai numerals and similar OCR confusions
    # '๖' is often confused with 'b' or '6', so try both replacements
    text = text.replace('๖', 'b') #.replace('๐', '0').replace('๑', '1').replace('๙', '9')
   #  # Also try replacing '๖' with '6' if needed (for numeric IDs)
   #  text = re.sub(r'([a-zA-Z0-9])b([a-zA-Z0-9])', r'\g<1>6\g<2>', text)
    return text

def extract_url_from_image(image: Image.Image) -> str:
    width, height = image.size
    crop_box = (0, int(height * 0.95), width, height)
    cropped = image.crop(crop_box)
    cropped = preprocess_image(cropped, save_path='debug_url_zone_preprocessed.png', upscale=6, contrast=1.1, threshold=150, sharpen=False)
    url_text = reader.readtext(np.array(cropped), detail=0, contrast_ths=0.05, adjust_contrast=0.7)
    url_text = ' '.join(url_text)
    url_text_clean = url_text.replace(' ', '').replace('|', '').replace('\n', '').replace('\r', '')
    url_text_clean = fix_common_ocr_errors(url_text_clean)
    match = re.search(r'https?[:/ ]+([a-zA-Z0-9.\-_]+)[/a-zA-Z0-9.\-_]+', url_text_clean)
    if match:
        url = url_text_clean[url_text_clean.find('http'):]
        url = url.replace(':/', '://').replace(' ', '').replace('|', '')
        url = re.split(r'[^a-zA-Z0-9:/._\-]', url)[0]
        return url
    # Fallback: OCR the whole image if not found in cropped area
    full_img = preprocess_image(image, save_path='debug_full_preprocessed.png', upscale=2, contrast=1.2, threshold=160, sharpen=False)
    full_text = reader.readtext(np.array(full_img), detail=0, contrast_ths=0.05, adjust_contrast=0.7)
    full_text = ' '.join(full_text)
    full_text_clean = full_text.replace(' ', '').replace('|', '').replace('\n', '').replace('\r', '')
    full_text_clean = fix_common_ocr_errors(full_text_clean)
    match_full = re.search(r'https?[:/ ]+([a-zA-Z0-9.\-_]+)[/a-zA-Z0-9.\-_]+', full_text_clean)
    if match_full:
        url = full_text_clean[full_text_clean.find('http'):]
        url = url.replace(':/', '://').replace(' ', '').replace('|', '')
        url = re.split(r'[^a-zA-Z0-9:/._\-]', url)[0]
        return url
    return ''

def extract_fields_from_image(image: Image.Image) -> dict:
    preprocessed_image = preprocess_image(image, save_path='debug_full_preprocessed.png', upscale=2, contrast=1.2, threshold=160, sharpen=False)
    image_np = np.array(preprocessed_image)
    results = reader.readtext(image_np, detail=0, contrast_ths=0.05, adjust_contrast=0.7)
    full_text = " ".join(results)
    full_text = fix_common_ocr_errors(full_text)
    logger.info("🧠 OCR Full Text:\n" + full_text)

    # Extract fields
    name_match = re.search(r"presented to\s+(.+)", full_text, re.IGNORECASE)
    student_name = name_match.group(1).strip() if name_match else ""

    course_match = re.search(r"completed the Open Online Course\s+(.+)", full_text, re.IGNORECASE)
    course_name = course_match.group(1).strip() if course_match else ""

    date_match = re.search(r"On\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", full_text, re.IGNORECASE)
    course_date = date_match.group(1).strip() if date_match else ""

    url = extract_url_from_image(image)

    fields = {
        "student_name": student_name,
        "course_name": course_name,
        "date": course_date,
        "url": url
    }
    logger.info("✅ Fields Extracted: " + str(fields))
    return fields

@app.post("/ocr", summary="Extract information from certificate image", description="Upload a certificate image to extract student name, course name, date, and certificate URL")
async def ocr_certificate(file: UploadFile = File(...)):
    logger.info(f"🚀 [FastAPI] Processing OCR request for file: {file.filename}")
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only image files are allowed."
            )
        contents = await file.read()
        logger.info(f"📥 Received file: {file.filename} ({len(contents)} bytes)")
        try:
            image = Image.open(io.BytesIO(contents))
            logger.info(f"Image loaded successfully: {image.size} {image.mode}")
        except Exception as e:
            logger.error(f"Failed to load image: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to load image: {str(e)}"
            )
        try:
            fields = extract_fields_from_image(image)
            logger.info("✅ Fields extracted successfully")
            return {
                "status": "success",
                "data": fields
            }
        except Exception as e:
            logger.error(f"Failed to extract fields: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract fields from image: {str(e)}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_deep_ocr:app", host="0.0.0.0", port=8000, reload=True) 