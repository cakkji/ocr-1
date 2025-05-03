import spacy
from spacy.training.example import Example
import random
import uuid
from faker import Faker

# เรียกใช้ faker ภาษาอังกฤษ
fake = Faker()

# Load base model
nlp = spacy.load("en_core_web_sm")


# สร้างชุดข้อมูล
TRAIN_DATA = []

# คอร์สตัวอย่าง
courses = [
    "Data Science Essentials",
    "Advanced Python Programming",
    "AI for Everyone",
    "Machine Learning with Scikit-learn",
    "Deep Learning Foundations",
    "Cyber Security Fundamentals",
    "Natural Language Processing",
    "Computer Vision Basics"
]

# URL prefix
url_base = [
    "https://mooc.buu.ac.th/certificates/",
    "https://certs.university.edu/",
    "https://example.org/cert/"
]

# Templates หลากหลาย
templates = [
    "Certificate awarded to {name} for completing the course {course} on {date}. Certificate: {url}",
    "This is to certify that {name} has successfully finished {course}. Date: {date} Link: {url}",
    "Presented to {name} for course: {course} completed on {date}. Ref: {url}",
    "CERTIFICATE\nName: {name}\nCourse: {course}\nCompletion Date: {date}\n{url}",
    "Certified for completing '{course}' by {name} on {date}. Download: {url}",
    "To: {name}\nCourse Taken: {course}\nDate Issued: {date}\nCertificate Link: {url}",
    "{name} completed the program '{course}'\nIssued: {date}\nCert#: {url}",
    "Name >> {name}\nCourse >> {course}\nDate >> {date}\n{url}"
]

templates += [

    # ไม่มีคำบอกชื่อ field
    "{name}\n{course}\n{date}\n{url}",

    # เรียงลำดับใหม่
    "Issued on {date} to {name} for {course}. Certificate ref: {url}",

    # คำศัพท์แปลก
    "This document certifies that {name} attended the program titled '{course}' dated {date}. View: {url}",

    # ภาษาเป็นทางการแบบกระชับ
    "Participant: {name}, Course: {course}, Date of Issue: {date}, Ref URL: {url}",

    # เรียงสลับ + ไม่มีหัวเรื่อง
    "{course} completed by {name}, dated {date}. Check: {url}",

    # format แบบที่อาจเจอจาก OCR
    "CERTIFICATE||{name}||{course}||{date}||{url}",

    # รูปแบบยาว ๆ แบบเรียงหลายย่อหน้า
    "This is to officially acknowledge that the individual named {name} has fulfilled the requirements of the course titled {course}. The certificate was issued on {date}. Access your certificate at: {url}"
]


# 🔧 ฟังก์ชันช่วย annotate entity
def annotate_entities(text: str, name: str, course: str, date: str, url: str):
    entities = []
    for val, label in [(name, "PERSON"), (course, "COURSE"), (date, "DATE"), (url, "URL")]:
        start = text.find(val)
        end = start + len(val)
        if start != -1:
            entities.append((start, end, label))
    return (text, {"entities": entities})


# 🎯 สร้างตัวอย่างข้อมูล 100 ชุด
for _ in range(600):
    name = fake.name()
    course = random.choice(courses)
    date = fake.date_this_decade().strftime("%B %d, %Y")
    url = random.choice(url_base) + uuid.uuid4().hex

    template = random.choice(templates)
    text = template.format(name=name, course=course, date=date, url=url)

    TRAIN_DATA.append(annotate_entities(text, name, course, date, url))

# ✅ ดูตัวอย่างที่สร้างได้
for sample in TRAIN_DATA[:2]:
    print("\nTEXT:\n", sample[0])
    print("ENTITIES:\n", sample[1]["entities"])




# Disable other pipelines
pipe_exceptions = ["ner"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

# Training loop
from spacy.util import minibatch, compounding

with nlp.disable_pipes(*unaffected_pipes):
    optimizer = nlp.resume_training()
    for iteration in range(50):
        random.shuffle(TRAIN_DATA)
        losses = {}
        batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
        for batch in batches:
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], drop=0.5, losses=losses)
        print(f"Losses at iteration {iteration}: {losses}")

# Save model
nlp.to_disk("./certificate_ner_model")
print("✅ Model saved")
