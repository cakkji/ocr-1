from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pdf2image import convert_from_bytes
from PIL import Image, ImageFilter
import pytesseract
import re
import io
import unicodedata
from fuzzywuzzy import fuzz, process
import requests
from bs4 import BeautifulSoup

# เปลี่ยนตาม OS ถ้าใช้บน Ubuntu ไม่ต้องเซ็ต path
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

course_db = {
    "ภาษาอังกฤษเพื่อการสื่อสาร (English for Communication)": 10,
    "Experiential English": 12,
    "การประยุกต์ใช้ Generative AI ในการทำงาน": 15,
    "การประยุกต์ใช้ Collaboration tools ในการเพิ่มประสิทธิภาพในการทำงานและประสานงานภายในองค์กร": 14,
    "Data Visualization with Tableau Desktop": 14
    
}

def validate_url(url: str) -> bool:
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

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

def extract_course_from_url_text(text: str):
    lines = text.split("\n")
    found = ""
    for line in lines:
        if "collaboration" in line.lower() or "การประยุกต์ใช้" in line:
            found += line.strip() + " "
    return found.strip()

def compare_with_url_data(url, ocr_name, ocr_course):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return False, "", ""

        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        print("🌐 Raw text จาก URL:\n", text)

        name_match = fuzz.partial_ratio(ocr_name.lower(), text.lower()) > 90
        course_from_url = extract_course_from_url_text(text)
        course_match = fuzz.partial_ratio(ocr_course.lower(), course_from_url.lower()) > 90

        return name_match and course_match, course_from_url, text
    except Exception as e:
        print("❌ Error checking URL:", e)
        return False, "", ""

def extract_url_from_image(image: Image.Image):
    width, height = image.size
    cropped = image.crop((0, int(height * 0.92), int(width * 0.5), height))
    cropped = cropped.resize((cropped.width * 3, cropped.height * 3))
    cropped = cropped.convert("L")
    cropped = cropped.point(lambda x: 0 if x < 180 else 255, '1')
    cropped = cropped.filter(ImageFilter.SHARPEN)

    config = "--psm 7 --oem 3"
    text = pytesseract.image_to_string(cropped, lang="eng", config=config)

    cleaned = text.replace(" ", "").replace("|", "").replace("\n", "").strip()
    cleaned = re.sub(r'O', '0', cleaned)
    cleaned = re.sub(r'¢', 'c', cleaned)

    base_match = re.search(r'(https?://[a-zA-Z0-9./_\-]+/certificates/)', cleaned)
    uuid_parts = re.findall(r'[a-fA-F0-9]{4,}', cleaned)
    joined_uuid = ''.join(uuid_parts)

    if base_match and len(joined_uuid) >= 32:
        return base_match.group(1) + joined_uuid[:32]
    return ""

def extract_fields_from_image(image: Image.Image):
    text = pytesseract.image_to_string(image, lang="eng+tha")

    # OCR จาก full text
    direct_url_match = re.search(r'https?://[^\s]+', text)
    direct_url = re.sub(r'O', '0', direct_url_match.group(0)) if direct_url_match else ""

    final_url = direct_url if validate_url(direct_url) else extract_url_from_image(image)

    name_match = re.search(r"presented to\s+(.+)", text)
    student_name = name_match.group(1).strip() if name_match else ""

    # รวมหลายบรรทัดเป็นชื่อวิชา
    course_lines = re.findall(r"completed the Open Online Course\s+(.+)", text)
    course_raw = course_lines[0].strip() if course_lines else ""
    course_raw += "\n" + "\n".join(re.findall(r"^[\u0E00-\u0E7F\sA-Za-z0-9]+$", text, re.MULTILINE))

    course_raw = course_raw.strip()
    course_name = fuzzy_match_course_name(course_raw)

    date_match = re.search(r"On\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", text)
    course_date = date_match.group(1).strip() if date_match else ""

    verified, url_course, _ = compare_with_url_data(final_url, student_name, course_name)

    # ถ้า course OCR เพี้ยนเกินไป → ใช้ course จากหน้าเว็บแทน
    if not verified and url_course:
        score = fuzz.partial_ratio(course_name.lower(), url_course.lower())
        if score < 60:
            print("⚠️ เปลี่ยนชื่อวิชาจาก URL:", url_course)
            course_name = url_course

    return {
        "student_name": student_name,
        "course_name": course_name,
        "date": course_date,
        "url": final_url,
        "verified": verified
    }

@app.post("/ocr")
async def ocr_certificate(file: UploadFile = File(...)):
    filename = file.filename.lower()
    contents = await file.read()

    if filename.endswith(".pdf"):
        images = convert_from_bytes(contents, dpi=400)
        image = images[0]
    else:
        image = Image.open(io.BytesIO(contents))

    fields = extract_fields_from_image(image)
    return {"status": "success", "data": fields}
