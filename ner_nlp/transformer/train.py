from gliner import GLiNER

model = GLiNER.from_pretrained("urchade/gliner-base")  # หรือ "gliner-large"

text = "นายวิชัย ส่องแสง สำเร็จการศึกษาหลักสูตร Deep Learning เมื่อวันที่ 12 เมษายน 2567"
labels = ["ชื่อคน", "ชื่อหลักสูตร", "วันออกประกาศ"]

results = model.predict_entities(text, labels)
print(results)
