//index.js
const express = require('express');
const app = express();
const cors = require('cors');

app.use(cors({
  origin: 'http://localhost:9000',  // ให้ตรงกับที่ Quasar ใช้งานจริง
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));



// ✅ เพิ่ม middleware ตรงนี้
app.use(express.json())

const ocrRoutes = require('./routes/ocr');
app.use('/api/ocr', ocrRoutes);

app.listen(3000, () => {
  console.log('🟢 Server running on http://localhost:3000');
});