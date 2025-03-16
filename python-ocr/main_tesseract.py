
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import re
import io
import unicodedata
from fuzzywuzzy import fuzz, process

app = FastAPI()

# 💡 ระบุ path ไปยัง tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ✅ เปิดให้ Frontend ใช้งาน API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Course database
course_db = {
    "ภาษาอังกฤษเพื่อการสื่อสาร (English for Communication)": 10,
    "Experiential English": 12,
    "การประยุกต์ใช้ Generative AI ในการทำงาน": 15,
}

def clean_text(text):
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", "", text)

def fuzzy_match_course_name(course_raw):
    cleaned_input = clean_text(course_raw)
    cleaned_keys = [clean_text(k) for k in course_db.keys()]
    best_match, score = process.extractOne(cleaned_input, cleaned_keys, scorer=fuzz.token_sort_ratio)
    if score > 40:
        return list(course_db.keys())[cleaned_keys.index(best_match)]
    return course_raw

def extract_fields_from_text(text):
    name_match = re.search(r"presented to\s+(.+)", text)
    student_name = name_match.group(1).strip() if name_match else ""

    course_match = re.search(r"completed the Open Online Course\s+(.+)", text)
    course_raw = course_match.group(1).strip() if course_match else ""
    course_name = fuzzy_match_course_name(course_raw)

    date_match = re.search(r"On\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
    course_date = date_match.group(1).strip() if date_match else ""

    return {
        "student_name": student_name,
        "course_name": course_name,
        "date": course_date
    }

@app.post("/ocr")
async def ocr_certificate(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    text = pytesseract.image_to_string(image, lang="eng+tha")
    fields = extract_fields_from_text(text)
    return {"status": "success", "data": fields}
