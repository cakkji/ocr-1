const express = require('express');
const router = express.Router();
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const upload = multer({ dest: 'uploads/' });

router.post('/upload', upload.single('file'), async (req, res) => {
  const form = new FormData();
  form.append('file', fs.createReadStream(req.file.path));

  try {
    const response = await axios.post('http://localhost:8000/ocr', form, {
      headers: form.getHeaders()
    });

    res.json(response.data); // ✅ ส่ง response กลับให้ frontend
  } catch (err) {
    console.error('❌ OCR proxy error:', err.message);
    res.status(500).json({ error: 'OCR failed', detail: err.message });
  }
});

// 📦 เพิ่มหลัง route /upload
router.post('/approve', (req, res) => {
  const { student_name, course_name, date } = req.body

  console.log('📥 รับข้อมูลอนุมัติจาก frontend:')
  console.log({ student_name, course_name, date })

  // ตัวอย่าง: เก็บประวัติ (ในอนาคตอาจต่อ DB)
  // ตรวจสอบข้อมูลก่อนอนุมัติ เช่น ซ้ำหรือไม่ ฯลฯ

  // ✅ ส่งกลับว่า success
  res.json({ status: 'approved' })
})


module.exports = router;
