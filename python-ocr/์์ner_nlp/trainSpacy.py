import spacy
from spacy.training.example import Example

# Load base model
nlp = spacy.load("en_core_web_sm")

# Add new labels
ner = nlp.get_pipe("ner")
ner.add_label("PERSON")
ner.add_label("COURSE")
ner.add_label("DATE")

# Training data
TRAIN_DATA = [
    # Layout 1
    (
        """CERTIFICATE OF COMPLETION
        This is to certify that
        Sahaphap Ritnetikul
        has successfully completed
        Experiential English
        on October 28, 2024
        https://mooc.buu.ac.th/certificates/abc12345""",
        {
            "entities": [
                (48, 68, "PERSON"),
                (95, 117, "COURSE"),
                (121, 137, "DATE"),
                (138, 185, "URL"),
            ]
        },
    ),

    # Layout 2
    (
        """Burapha University Language Institute
        presents this certificate to
        Jane Smith
        for completing the Open Online Course
        Data Visualization with Tableau
        Dated January 2025
        Certificate ID: 1234-5678-90
        """,
        {
            "entities": [
                (55, 65, "PERSON"),
                (99, 132, "COURSE"),
                (140, 152, "DATE"),
            ]
        },
    ),

    # Layout 3
    (
        """This certifies
        John Doe
        successfully finished the course
        Generative AI in Practice
        Dated: 12 March 2025
        https://cert.example.com/xyz98765
        """,
        {
            "entities": [
                (17, 25, "PERSON"),
                (55, 81, "COURSE"),
                (89, 102, "DATE"),
                (103, 139, "URL"),
            ]
        },
    ),

    # Layout 4
    (
        """CERTIFICATE
        Name: Yanisa Wongsawat
        Course: English for Communication
        Date: March 2025
        https://mooc.buu.ac.th/certificates/abcdef1234567890
        """,
        {
            "entities": [
                (12, 29, "PERSON"),
                (39, 67, "COURSE"),
                (74, 84, "DATE"),
                (85, 131, "URL"),
            ]
        },
    ),

    # Layout 5 (Shortened URL)
    (
        """Certified for
        Pasina Marunsawas
        in Data Science Essentials
        Date: Jan 2025
        Link: mooc.buu.ac.th/certificates/short1234
        """,
        {
            "entities": [
                (15, 34, "PERSON"),
                (38, 61, "COURSE"),
                (68, 77, "DATE"),
                (84, 123, "URL"),
            ]
        },
    ),

    # Layout 6 (Different phrasing)
    (
        """Awarded to
        Ananda Srisai
        for completing course:
        Advanced Python Programming
        Completion Date: February 2025
        """,
        {
            "entities": [
                (11, 25, "PERSON"),
                (50, 77, "COURSE"),
                (94, 108, "DATE"),
            ]
        },
    ),

    # Layout 7
    (
        """Certificate
        Student Name: Johnathan Lee
        Course Completed: Machine Learning Basics
        Date Completed: 2025-04-01
        https://university.org/certificates/mlbasics2025
        """,
        {
            "entities": [
                (20, 34, "PERSON"),
                (54, 81, "COURSE"),
                (99, 109, "DATE"),
                (110, 160, "URL"),
            ]
        },
    ),

    # Layout 8
    (
        """Official Certificate
        Presented to:
        Dr. Supanuthai It-ngam
        Completed Course: Data Analytics with Excel
        Completion Date: May 15, 2025
        Certificate Link: https://mooc.buu.ac.th/cert/xyz
        """,
        {
            "entities": [
                (25, 48, "PERSON"),
                (68, 99, "COURSE"),
                (116, 130, "DATE"),
                (149, 184, "URL"),
            ]
        },
    ),

    # Layout 9
    (
        """This is to certify the participation of
        Kritsada Phonchai
        in the course
        Practical Generative AI Tools
        Date Issued: December 2024
        """,
        {
            "entities": [
                (38, 55, "PERSON"),
                (74, 104, "COURSE"),
                (117, 132, "DATE"),
            ]
        },
    ),

    # Layout 10
    (
        """Certification
        Candidate: Pranee Sittichai
        Successfully completed:
        AI for Everyone
        Date: 01 February 2025
        Certificate URL: https://certs.site/ai12345
        """,
        {
            "entities": [
                (15, 32, "PERSON"),
                (57, 72, "COURSE"),
                (79, 95, "DATE"),
                (113, 145, "URL"),
            ]
        },
    ),
]

from faker import Faker
import random
import uuid

fake = Faker()
TRAIN_DATA = []

# 🎯 คอร์สและ URL base ที่จะสุ่ม
courses = [
    "Experiential English",
    "Generative AI in Practice",
    "Data Visualization with Tableau",
    "Machine Learning Basics",
    "AI for Everyone"
]
url_base = [
    "https://mooc.buu.ac.th/certificates/",
    "https://certs.example.com/",
    "https://university.org/certificates/"
]

# 🎯 Template แบบหลากหลาย Layout
templates = [
    """CERTIFICATE
This is to certify that {name}
has completed the course {course}
on {date}
{url}""",

    """Awarded to: {name}
Completed: {course}
Date: {date}
Link: {url}""",

    """This certifies {name}
successfully completed {course}
Dated {date}
Certificate URL: {url}""",

    """Certificate of Achievement
Presented to {name}
For completing: {course}
Date Issued: {date}
{url}"""
]

# 🚀 สร้าง 50 ตัวอย่าง
for _ in range(50):
    name = fake.name()
    course = random.choice(courses)
    date = fake.date_this_decade().strftime("%B %d, %Y")
    url = random.choice(url_base) + uuid.uuid4().hex

    template = random.choice(templates)
    text = template.format(name=name, course=course, date=date, url=url)

    # หา index ของแต่ละ entity
    start_name = text.find(name)
    end_name = start_name + len(name)

    start_course = text.find(course)
    end_course = start_course + len(course)

    start_date = text.find(date)
    end_date = start_date + len(date)

    start_url = text.find(url)
    end_url = start_url + len(url)

    TRAIN_DATA.append((
        text,
        {
            "entities": [
                (start_name, end_name, "PERSON"),
                (start_course, end_course, "COURSE"),
                (start_date, end_date, "DATE"),
                (start_url, end_url, "URL"),
            ]
        }
    ))

# ✅ ดูตัวอย่างที่สร้างได้
for sample in TRAIN_DATA[:2]:
    print("\nTEXT:\n", sample[0])
    print("ENTITIES:\n", sample[1]["entities"])




# Disable other pipelines
pipe_exceptions = ["ner"]
unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

# Training loop
import random
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
