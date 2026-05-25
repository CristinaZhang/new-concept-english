<template>
  <div class="lesson-detail" v-if="lesson">
    <button class="back-btn" @click="$router.push('/lessons')">← 返回</button>

    <h2 class="title">L{{ lesson.lesson_number }} {{ lesson.title }}</h2>

    <!-- Lesson image -->
    <div class="lesson-image" v-if="lesson.image_url">
      <img :src="lesson.image_url" :alt="lesson.title" />
    </div>

    <!-- Audio player -->
    <AudioPlayer v-if="lesson.audio_url" :src="lesson.audio_url" :label="audioLabel" />

    <!-- Lesson text -->
    <section class="section">
      <h3>📄 课文</h3>
      <pre class="lesson-text">{{ lesson.text }}</pre>
    </section>

    <!-- Translation -->
    <section class="section">
      <h3>🇨🇳 翻译</h3>
      <pre class="lesson-text translation">{{ lesson.translation }}</pre>
    </section>

    <!-- Vocabulary -->
    <section class="section" v-if="vocab.length">
      <h3>📝 生词</h3>
      <div class="vocab-list">
        <div class="vocab-item" v-for="v in vocab" :key="v.id">
          <span class="word">{{ v.word }}</span>
          <span class="phonetic">{{ v.phonetic }}</span>
          <span class="meaning">{{ v.meaning }}</span>
          <button class="speak-btn" @click="speakWord(v.word)" :title="`发音: ${v.word}`">🔊</button>
        </div>
      </div>
    </section>

    <!-- Grammar -->
    <section class="section" v-if="grammar.length">
      <h3>📐 语法点</h3>
      <div class="grammar-list">
        <div class="grammar-item" v-for="g in grammar" :key="g.id">
          <h4>{{ g.name }}</h4>
          <p>{{ g.explanation }}</p>
          <ul v-if="g.examples && g.examples.length">
            <li v-for="(ex, i) in g.examples" :key="i">{{ ex }}</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Exercises -->
    <section class="section" v-if="exercises.length">
      <h3>✏️ 练习</h3>
      <div class="exercise-list">
        <div class="exercise-item" v-for="ex in exercises" :key="ex.id">
          <p class="question">{{ ex.question }}</p>

          <!-- Multiple choice -->
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

          <!-- Fill blank -->
          <div class="fill-blank" v-else>
            <input
              v-model="inputAnswers[ex.id]"
              placeholder="输入你的答案"
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

          <!-- Result -->
          <div class="result" v-if="results[ex.id]">
            <span :class="results[ex.id].correct ? 'correct' : 'incorrect'">
              {{ results[ex.id].correct ? '✅ 正确!' : `❌ 正确答案: ${results[ex.id].correct_answer}` }}
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Navigation -->
    <div class="nav-buttons">
      <button
        v-if="lesson.lesson_number > 1"
        class="nav-btn"
        @click="$router.push(`/lessons/${lesson.lesson_number - 1}`)"
      >
        ← 上一课
      </button>
      <button class="nav-btn" @click="$router.push(`/lessons/${lesson.lesson_number + 1}`)">
        下一课 →
      </button>
    </div>
  </div>

  <div v-else-if="loading" class="loading">加载中...</div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  getLesson,
  getLessonVocabulary,
  getLessonGrammar,
  getExercises,
  submitExercise,
  updateProgress,
} from '../api/index.js'
import AudioPlayer from '../components/AudioPlayer.vue'

const route = useRoute()
const lesson = ref(null)
const vocab = ref([])
const grammar = ref([])
const exercises = ref([])
const loading = ref(true)
const results = reactive({})
const answered = reactive({})
const inputAnswers = reactive({})
const exerciseScores = reactive({})

// Audio label — note paired audio for even lessons
const audioLabel = computed(() => {
  if (!lesson.value) return '课文音频'
  const n = lesson.value.lesson_number
  if (n % 2 === 0) {
    return `课文音频 (L${n - 1}&L${n} 合并)`
  }
  return `课文音频 (L${n}&L${n + 1} 合并)`
})

// Web Speech API — word pronunciation
function speakWord(word) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(word)
  utterance.lang = 'en-US'
  utterance.rate = 0.8
  window.speechSynthesis.speak(utterance)
}

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

    // Track score
    if (!exerciseScores[exercise.id]) exerciseScores[exercise.id] = {}
    exerciseScores[exercise.id].total = (exerciseScores[exercise.id].total || 0) + 1
    if (res.data.correct) {
      exerciseScores[exercise.id].correct = (exerciseScores[exercise.id].correct || 0) + 1
    }

    // Update progress after all exercises done
    const totalEx = exercises.value.length
    const answeredCount = Object.keys(answered).length
    if (answeredCount === totalEx) {
      const totalCorrect = Object.values(exerciseScores).reduce((s, e) => s + (e.correct || 0), 0)
      const totalAttempts = Object.values(exerciseScores).reduce((s, e) => s + (e.total || 0), 0)
      const score = totalAttempts > 0 ? Math.round((totalCorrect / totalAttempts) * 100) : 0
      await updateProgress(lesson.value.id, { grammar_score: score })
    }
  } catch (e) {
    console.error('Failed to submit answer:', e)
  }
}

onMounted(async () => {
  const id = route.params.id
  try {
    const [lessonRes, vocabRes, grammarRes, exRes] = await Promise.all([
      getLesson(id),
      getLessonVocabulary(id),
      getLessonGrammar(id),
      getExercises(id),
    ])
    lesson.value = lessonRes.data
    vocab.value = vocabRes.data
    grammar.value = grammarRes.data
    exercises.value = exRes.data
  } catch (e) {
    console.error('Failed to load lesson:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.back-btn {
  background: none;
  border: none;
  color: #4a90d9;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 4px 0;
  margin-bottom: 12px;
}

.title {
  font-size: 1.3rem;
  margin-bottom: 16px;
  color: #333;
}

.lesson-image {
  margin-bottom: 16px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.lesson-image img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  display: block;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.section h3 {
  font-size: 1.05rem;
  margin-bottom: 12px;
  color: #4a90d9;
}

.lesson-text {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 1rem;
  font-family: inherit;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}

.translation {
  color: #666;
}

.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vocab-item {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.vocab-item .word {
  font-weight: 600;
  min-width: 80px;
}

.vocab-item .phonetic {
  color: #888;
  font-size: 0.85rem;
  min-width: 100px;
}

.vocab-item .meaning {
  flex: 1;
}

.speak-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.speak-btn:hover {
  background: #f0f7ff;
}

.grammar-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.grammar-item h4 {
  font-size: 1rem;
  margin-bottom: 4px;
}

.grammar-item p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 8px;
}

.grammar-item ul {
  margin-left: 20px;
  color: #666;
}

.grammar-item li {
  margin-bottom: 4px;
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
  transition: all 0.2s;
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

.nav-buttons {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 20px;
}

.nav-btn {
  flex: 1;
  padding: 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  color: #4a90d9;
  font-size: 0.95rem;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
