<template>
  <q-page class="q-pa-md">
    <q-card>
      <q-card-section>
        <div class="text-h6">อัปโหลดใบ Certificate</div>
        <q-uploader
          label="อัปโหลดไฟล์ PDF หรือ PNG"
          url="http://localhost:3000/api/ocr/upload"
          accept=".pdf,image/*"
          :auto-upload="true"
          field-name="file"
          @uploaded="onUploaded"
        />
      </q-card-section>
      <q-separator />
      <q-card-section v-if="ocrResult">
        <q-markup-table>
          <tbody>
            <tr>
              <td><b>ชื่อ 555</b></td>
              <td>{{ ocrResult.student_name }}</td>
            </tr>
            <tr>
              <td><b>วิชา</b></td>
              <td>{{ ocrResult.course_name }}</td>
            </tr>
            <tr>
              <td><b>วันที่จบ</b></td>
              <td>{{ ocrResult.date }}</td>
            </tr>
          </tbody>
        </q-markup-table>

        <q-btn label="อนุมัติ" color="primary" :loading="loading" @click="approve" />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'boot/axios'

const ocrResult = ref(null)
const loading = ref(false)

/*function parseDonutResult(raw) {
  const name = raw.match(/<s_name>(.*?)<\/s_name>/)?.[1] || ''
  const course = raw.match(/<s_course>(.*?)<\/s_course>/)?.[1] || ''
  const date = raw.match(/<s_date>(.*?)<\/s_date>/)?.[1] || ''
  return { name, course, date }
}*/

function onUploaded({ xhr }) {
  const res = JSON.parse(xhr.response)

  console.log('📦 RAW:', res)

  const parsed = res.data // ✅ รับข้อมูลจาก FastAPI
  console.log('✅ Parsed:', parsed)

  ocrResult.value = parsed
}

function approve() {
  loading.value = true

  // 🔥 แก้ตรงนี้
  const payload = JSON.parse(JSON.stringify(ocrResult.value))

  console.log('📥 ข้อมูลที่จะส่งไป backend:', payload)

  api
    .post('/ocr/approve', payload) // ✅ ถูกต้อง

    .then(() => {
      alert('✅ เพิ่มชั่วโมงสำเร็จ!')
    })
    .catch((err) => {
      console.error('❌ Failed to approve:', err)
      alert('❌ ไม่สามารถเพิ่มชั่วโมงได้')
    })
    .finally(() => {
      loading.value = false
    })
}
</script>
