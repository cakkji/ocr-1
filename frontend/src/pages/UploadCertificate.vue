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
              <td class="text-bold">👤 ชื่อนิสิต</td>
              <td>{{ ocrResult.student_name }}</td>
            </tr>
            <tr>
              <td class="text-bold">📘 วิชา</td>
              <td style="white-space: pre-line">
                {{ formatCourseName(ocrResult.course_name) }}
              </td>
            </tr>
            <tr>
              <td class="text-bold">🗓️ วันที่</td>
              <td>{{ ocrResult.date }}</td>
            </tr>
            <tr v-if="ocrResult.url">
              <td class="text-bold">🔗 ลิงก์ Certificate</td>
              <td>
                <a :href="ocrResult.url" target="_blank">{{ ocrResult.url }}</a>
              </td>
            </tr>
          </tbody>
        </q-markup-table>

        <!-- หมายเหตุผลการตรวจสอบ -->
        <div class="q-mt-sm">
          <q-banner
            v-if="ocrResult.verified"
            class="bg-green-2 text-green-9"
            rounded
            icon="check_circle"
          >
            ✔️ ข้อมูลในใบประกาศ <b>ตรงกับข้อมูลใน URL</b>
          </q-banner>

          <q-banner
            v-else-if="ocrResult.url && !ocrResult.verified"
            class="bg-orange-2 text-orange-10"
            rounded
            icon="warning"
          >
            ⚠️ ข้อมูลในใบที่อัปโหลด <b>ไม่ตรงกับใน URL</b> เช่น ชื่อหรือชื่อวิชาแตกต่าง
            <div v-if="ocrResult.verify_note" class="q-mt-xs text-caption">
              หมายเหตุ: {{ ocrResult.verify_note }}
            </div>
          </q-banner>

          <q-banner v-else class="bg-red-2 text-red-10" rounded icon="error">
            ❌ ไม่สามารถตรวจสอบกับ URL ได้ (อาจไม่มี URL หรือลิงก์ไม่เปิด)
          </q-banner>
        </div>

        <q-btn
          label="อนุมัติ"
          color="primary"
          :loading="loading"
          :disable="loading || !ocrResult"
          @click="approve"
          class="q-mt-md"
        />
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script setup>
import { ref } from 'vue'
import { api } from 'boot/axios'

const ocrResult = ref(null)
const loading = ref(false)

function formatCourseName(raw) {
  if (!raw) return ''
  return raw
    .replace(/([ก-๙])\s(?=[ก-๙])/g, '$1') // ลบ space ระหว่างพยัญชนะไทย
    .replace(/\s{2,}/g, ' ') // ลบ space ซ้ำ
    .trim()
}

function onUploaded({ xhr }) {
  const res = JSON.parse(xhr.response)
  console.log('📦 RAW:', res)
  const parsed = res.data
  console.log('✅ Parsed:', parsed)
  ocrResult.value = parsed
}

function approve() {
  loading.value = true
  const payload = JSON.parse(JSON.stringify(ocrResult.value))
  console.log('📥 ข้อมูลที่จะส่งไป backend:', payload)

  api
    .post('/ocr/approve', payload)
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
