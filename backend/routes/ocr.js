//ocr.js
const express = require('express');
const router = express.Router();
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const upload = multer({ dest: 'uploads/' });

router.post('/upload', upload.single('file'), async (req, res) => {
  console.log("📥 [Express] ได้รับไฟล์จาก Quasar:", req.file);

  // ✅ ตรวจ path ของไฟล์ที่ Multer เซฟไว้
  console.log("🛠 Path ที่จะส่ง:", req.file?.path);

  const form = new FormData();
  form.append('file', fs.createReadStream(req.file.path));

  try {
    console.log("🚀 กำลังส่งต่อไป FastAPI /ocr...");
    const response = await axios.post('http://localhost:8001/ocr', form, {
      headers: form.getHeaders()
    });

    console.log('📦 Response from FastAPI:', response.data);
    res.json(response.data);
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

const checkUrlValid = async (url) => {
  try {
    const res = await axios.head(url);
    return res.status === 200;
  } catch {
    return false;
  }
}


module.exports = router;