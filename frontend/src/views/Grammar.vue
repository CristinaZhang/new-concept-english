<template>
  <div class="grammar-view">
    <h2 class="page-title">📐 语法学习</h2>

    <!-- Lesson selector -->
    <div class="lesson-selector">
      <select v-model="selectedLessonId" @change="loadGrammar">
        <option value="" disabled>选择课文</option>
        <option v-for="l in lessons" :key="l.id" :value="l.id">
          L{{ l.lesson_number }} - {{ l.title }}
        </option>
      </select>
    </div>

    <!-- Grammar points -->
    <div v-if="grammarPoints.length" class="grammar-points">
      <div class="grammar-card" v-for="g in grammarPoints" :key="g.id">
        <h3>{{ g.name }}</h3>
        <p class="explanation">{{ g.explanation }}</p>
        <ul v-if="g.examples && g.examples.length">
          <li v-for="(ex, i) in g.examples" :key="i">{{ ex }}</li>
        </ul>
      </div>
    </div>

    <!-- Exercises for this lesson -->
    <div v-if="exercises.length" class="exercises-section">
      <h3>✏️ 语法练习</h3>
      <div class="exercise-list">
        <div class="exercise-item" v-for="ex in exercises" :key="ex.id">
          <p class="question">{{ ex.question }}</p>

          <div class="options" v-if="ex.type === 'mc' && ex.options.length">
            <button
              v-for="opt in ex.options"
              :key="opt"
              class="option-btn"
              :class="getOptionClass(ex.id, opt)"
              @click="submitAnswer(ex, opt)"
              :disabled="answered[ex.id]"
            >
              {{ opt }}
            </button>
          </div>

          <div class="fill-blank" v-else>
            <input
              v-model="inputAnswers[ex.id]"
              placeholder="输入答案"
              @keyup.enter="submitAnswer(ex, inputAnswers[ex.id])"
              :disabled="answered[ex.id]"
            />
            <button
              class="submit-btn"
              @click="submitAnswer(ex, inputAnswers[ex.id])"
              :disabled="answered[ex.id] || !inputAnswers[ex.id]"
            >
              提交
            </button>
          </div>

          <div class="result" v-if="results[ex.id]">
            <span :class="results[ex.id].correct ? 'correct' : 'incorrect'">
              {{ results[ex.id].correct ? '✅ 正确!' : `❌ 正确答案: ${results[ex.id].correct_answer}` }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="selectedLessonId && !loading" class="empty">本课暂无语法内容。</div>
    <div v-else-if="loading" class="loading">加载中...</div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getLessons, getLessonGrammar, getExercises, submitExercise } from '../api/index.js'

const lessons = ref([])
const selectedLessonId = ref('')
const grammarPoints = ref([])
const exercises = ref([])
const loading = ref(false)
const results = reactive({})
const answered = reactive({})
const inputAnswers = reactive({})

function getOptionClass(exerciseId, option) {
  if (!answered[exerciseId]) return ''
  const r = results[exerciseId]
  if (r.correct && option === r.user_answer) return 'selected-correct'
  if (!r.correct && option === r.correct_answer) return 'show-correct'
  if (!r.correct && option === r.user_answer) return 'selected-wrong'
  return ''
}

async function submitAnswer(exercise, answer) {
  if (answered[exercise.id] || !answer) return
  try {
    const res = await submitExercise(exercise.id, answer.trim())
    results[exercise.id] = res.data
    answered[exercise.id] = true
  } catch (e) {
    console.error('Failed to submit:', e)
  }
}

async function loadGrammar() {
  if (!selectedLessonId) return
  loading.value = true
  results.value = {}
  answered.value = {}
  inputAnswers.value = {}
  try {
    const [grammarRes, exRes] = await Promise.all([
      getLessonGrammar(selectedLessonId),
      getExercises(selectedLessonId),
    ])
    grammarPoints.value = grammarRes.data
    exercises.value = exRes.data
  } catch (e) {
    console.error('Failed to load grammar:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const res = await getLessons({ limit: 144, offset: 0 })
    lessons.value = res.data.items
    // Auto-select first lesson
    if (lessons.value.length > 0) {
      selectedLessonId.value = lessons.value[0].id
      loadGrammar()
    }
  } catch (e) {
    console.error('Failed to load lessons:', e)
  }
})
</script>

<style scoped>
.page-title {
  font-size: 1.4rem;
  margin-bottom: 16px;
}

.lesson-selector select {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  background: white;
  outline: none;
  margin-bottom: 20px;
}

.lesson-selector select:focus {
  border-color: #4a90d9;
}

.grammar-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}

.grammar-card h3 {
  font-size: 1.05rem;
  color: #4a90d9;
  margin-bottom: 8px;
}

.grammar-card .explanation {
  color: #555;
  line-height: 1.6;
  margin-bottom: 12px;
}

.grammar-card ul {
  margin-left: 20px;
  color: #666;
}

.grammar-card li {
  margin-bottom: 4px;
}

.exercises-section {
  margin-top: 24px;
}

.exercises-section h3 {
  font-size: 1.05rem;
  margin-bottom: 12px;
  color: #333;
}

.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exercise-item .question {
  font-weight: 500;
  margin-bottom: 10px;
  white-space: pre-line;
}

.options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.option-btn {
  padding: 8px 20px;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: white;
  font-size: 0.95rem;
  cursor: pointer;
}

.option-btn:not(:disabled):hover {
  border-color: #4a90d9;
  background: #f0f7ff;
}

.option-btn.selected-correct {
  border-color: #4caf50;
  background: #e8f5e9;
  color: #2e7d32;
}

.option-btn.selected-wrong {
  border-color: #f44336;
  background: #ffebee;
  color: #c62828;
}

.option-btn.show-correct {
  border-color: #4caf50;
  background: #e8f5e9;
}

.fill-blank {
  display: flex;
  gap: 8px;
}

.fill-blank input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
  outline: none;
}

.fill-blank input:focus {
  border-color: #4a90d9;
}

.submit-btn {
  padding: 8px 16px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.5;
}

.result {
  margin-top: 8px;
  font-size: 0.9rem;
}

.correct {
  color: #4caf50;
  font-weight: 600;
}

.incorrect {
  color: #f44336;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
