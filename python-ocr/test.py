from PIL import Image, ImageFilter

img = Image.open("test5.png")
width, height = img.size

# ✅ Crop เฉพาะส่วนล่าง
cropped = img.crop((0, int(height * 0.92), width, height))  # หรือ 0.95 ถ้าลิงก์ต่ำมาก
cropped = cropped.filter(ImageFilter.SHARPEN)

# ✅ Save ภาพไว้ดู
cropped.save("debug_url_zone.png")

# ✅ แสดงภาพต้นฉบับและภาพที่ครอป
img.show()
cropped.show()
from PIL import Image
import pytesseract
import re

image = Image.open("debug_url_zone.png")
text = pytesseract.image_to_string(image, lang="eng", config="--psm 6")

print("🧾 Raw OCR:", text)

match = re.search(r'https?://[^\s\n]+', text)
print("✅ URL:", match.group(0) if match else "❌ ไม่พบลิงก์")
