<template>
  <div class="spelling-view">
    <h2 class="page-title">✏️ 拼写练习</h2>

    <div class="practice-area" v-if="currentWord">
      <!-- Show the meaning, user spells the word -->
      <div class="prompt-card">
        <p class="meaning">{{ currentWord.meaning }}</p>
        <p class="phonetic" v-if="currentWord.phonetic">{{ currentWord.phonetic }}</p>
        <p class="example" v-if="showHint && currentWord.example_sentence">
          💡 {{ currentWord.example_sentence }}
        </p>
      </div>

      <div class="input-area">
        <input
          ref="inputRef"
          v-model="userInput"
          placeholder="输入英文单词"
          @keyup.enter="checkSpelling"
          autocomplete="off"
          autocapitalize="off"
        />
        <button class="check-btn" @click="checkSpelling" :disabled="!userInput">
          检查
        </button>
      </div>

      <div class="feedback" v-if="result">
        <span :class="result.correct ? 'correct' : 'incorrect'">
          {{ result.correct ? '🎉 拼写正确!' : `❌ 正确拼写: ${currentWord.word}` }}
        </span>
      </div>

      <div class="controls">
        <button class="hint-btn" @click="showHint = true" v-if="!showHint">提示</button>
        <button class="skip-btn" @click="nextWord">跳过 →</button>
      </div>

      <div class="score-bar">
        <span>得分: {{ score }}/{{ attempts }}</span>
        <button class="reset-btn" @click="resetPractice">重新开始</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading">加载单词中...</div>
    <div v-else class="empty">暂无词汇数据，请先导入种子数据。</div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { getLessons, getLessonVocabulary } from '../api/index.js'

const words = ref([])
const currentIndex = ref(0)
const loading = ref(true)
const userInput = ref('')
const result = ref(null)
const showHint = ref(false)
const score = ref(0)
const attempts = ref(0)
const inputRef = ref(null)

const currentWord = ref(null)

function nextWord() {
  if (words.value.length === 0) return
  currentIndex.value = Math.floor(Math.random() * words.value.length)
  currentWord.value = words.value[currentIndex.value]
  userInput.value = ''
  result.value = null
  showHint.value = false
  nextTick(() => inputRef.value?.focus())
}

function checkSpelling() {
  if (!userInput.value.trim() || !currentWord.value) return
  attempts.value++
  const isCorrect = userInput.value.trim().toLowerCase() === currentWord.value.word.toLowerCase()
  result.value = { correct: isCorrect }
  if (isCorrect) score.value++

  // Auto-advance after a short delay
  setTimeout(() => nextWord(), 1500)
}

function resetPractice() {
  score.value = 0
  attempts.value = 0
  nextWord()
}

onMounted(async () => {
  try {
    const lessonsRes = await getLessons({ limit: 144, offset: 0 })
    const lessonIds = lessonsRes.data.items.map(l => l.id)
    const vocabPromises = lessonIds.map(id => getLessonVocabulary(id))
    const vocabResults = await Promise.allSettled(vocabPromises)

    words.value = vocabResults
      .filter(r => r.status === 'fulfilled')
      .flatMap(r => r.value.data)

    if (words.value.length > 0) {
      currentIndex.value = Math.floor(Math.random() * words.value.length)
      currentWord.value = words.value[currentIndex.value]
    }
  } catch (e) {
    console.error('Failed to load vocabulary:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-title {
  font-size: 1.4rem;
  margin-bottom: 16px;
}

.practice-area {
  text-align: center;
}

.prompt-card {
  background: white;
  border-radius: 16px;
  padding: 32px 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.meaning {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.phonetic {
  font-size: 1rem;
  color: #888;
  margin-bottom: 8px;
}

.example {
  font-size: 0.9rem;
  color: #4a90d9;
  margin-top: 12px;
}

.input-area {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 16px;
}

.input-area input {
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 1.1rem;
  width: 200px;
  text-align: center;
  outline: none;
}

.input-area input:focus {
  border-color: #4a90d9;
}

.check-btn {
  padding: 12px 24px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}

.check-btn:disabled {
  opacity: 0.5;
}

.feedback {
  margin-bottom: 16px;
  font-size: 1.1rem;
}

.correct {
  color: #4caf50;
  font-weight: 700;
}

.incorrect {
  color: #f44336;
  font-weight: 700;
}

.controls {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
}

.hint-btn, .skip-btn {
  padding: 8px 20px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
}

.score-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f0f7ff;
  border-radius: 10px;
  font-size: 0.9rem;
}

.reset-btn {
  padding: 6px 14px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
