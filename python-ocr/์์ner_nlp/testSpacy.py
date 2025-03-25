import spacy

# Load model ที่ train เสร็จแล้ว
nlp = spacy.load("./certificate_ner_model")

# ตัวอย่างข้อความใหม่
test_text = """
CERTIFICATE
This certifies John Doe
successfully completed Advanced Python Programming on February 12 2025 
Operator  John Doven
https://certs.example.com/abc12345
"""

# รัน Model
doc = nlp(test_text)

# แสดงผลลัพธ์
print("\n🔍 Extracted Entities:")
for ent in doc.ents:
    print(f"{ent.label_}: {ent.text}")
