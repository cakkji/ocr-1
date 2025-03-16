const fuzz = require('fuzzball')

// ดิกวิชาจริง
const courseList = [
  "ภาษาอังกฤษเพื่อการสื่อสาร (English for Communication)",
  "Experiential English",
  "การประยุกต์ใช้ Generative AI ในการทำงาน"
]

function fuzzyMatchCourse(input) {
  let best = { course: input, score: 0 }

  for (const course of courseList) {
    const score = fuzz.ratio(input, course)
    if (score > best.score) {
      best = { course, score }
    }
  }

  
  console.log(`🧠 Matching "${input}" → "${best.course}" (${best.score})`);
  return best.score > 80 ? best.course : input

}

module.exports = fuzzyMatchCourse
