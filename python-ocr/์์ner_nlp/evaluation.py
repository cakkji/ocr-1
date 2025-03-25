from spacy.training.example import Example
from spacy.scorer import Scorer

import spacy
# Load model ที่ train เสร็จแล้ว
nlp = spacy.load("./certificate_ner_model")


# Prepare Test Data
TEST_TEXT = """
CERTIFICATE
This certifies John Doe
successfully completed Advanced Python Programming
on February 12, 2025
https://certs.example.com/abc12345
"""

TEST_ANNOTATION = {
    "entities": [
        (28, 36, "PERSON"),  # John Doe
        (52, 81, "COURSE"),  # Advanced Python Programming
        (85, 102, "DATE"),   # February 12, 2025
        (103, 139, "URL"),   # URL
    ]
}

# # Convert to Example
# doc = nlp.make_doc(TEST_TEXT)
# example = Example.from_dict(doc, TEST_ANNOTATION)

# # Evaluate
# scorer = Scorer()
# results = scorer.score([example])

# print("\n📊 Evaluation Results:")
# print(f"Precision: {results['ents_p']:.2f}%")
# print(f"Recall: {results['ents_r']:.2f}%")
# print(f"F1 Score: {results['ents_f']:.2f}%")

for start, end, label in TEST_ANNOTATION['entities']:
    print(f"Entity: {label}, Text: '{TEST_TEXT[start:end]}'")

