<template>
  <div class="vocabulary-view">
    <h2 class="page-title">📝 词汇学习</h2>

    <!-- Flashcard mode -->
    <div class="flashcard-area" v-if="currentWord">
      <Flashcard :item="currentWord" />
      <div class="speak-row">
        <button class="speak-btn" @click="speakWord(currentWord.word)">
          🔊 听发音
        </button>
      </div>
      <div class="card-controls">
        <button class="nav-btn" @click="prevWord" :disabled="currentIndex === 0">上一词</button>
        <span class="card-counter">{{ currentIndex + 1 }} / {{ words.length }}</span>
        <button class="nav-btn" @click="nextWord" :disabled="currentIndex >= words.length - 1">下一词</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading">加载中...</div>
    <div v-else class="empty">暂无词汇数据。</div>

    <!-- Lesson filter -->
    <div class="lesson-filter" v-if="words.length">
      <select v-model="selectedLesson" @change="filterWords">
        <option value="all">全部课文</option>
        <option v-for="l in lessonList" :key="l.id" :value="l.id">
          L{{ l.lesson_number }} - {{ l.title }}
        </option>
      </select>
    </div>

    <!-- Word list toggle -->
    <details class="word-list-toggle">
      <summary>查看全部词汇列表（{{ displayWords.length }}个）</summary>
      <div class="word-table" v-if="displayWords.length">
        <div class="word-row" v-for="w in displayWords" :key="w.id" @click="jumpTo(w)">
          <span class="w-word">{{ w.word }}</span>
          <span class="w-phonetic">{{ w.phonetic }}</span>
          <span class="w-meaning">{{ w.meaning }}</span>
          <button class="speak-btn-small" @click.stop="speakWord(w.word)" :title="`发音: ${w.word}`">🔊</button>
        </div>
      </div>
    </details>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getLessons, getLessonVocabulary } from '../api/index.js'
import Flashcard from '../components/Flashcard.vue'

const allWords = ref([])
const lessonList = ref([])
const loading = ref(true)
const currentIndex = ref(0)
const selectedLesson = ref('all')

const words = computed(() => allWords.value)
const currentWord = computed(() => words.value[currentIndex.value] || null)

const displayWords = computed(() => {
  if (selectedLesson.value === 'all') return words.value
  return words.value.filter(w => w.lesson_id === selectedLesson.value)
})

function filterWords() {
  if (selectedLesson.value === 'all') {
    currentIndex.value = 0
  } else {
    currentIndex.value = 0
  }
}

function nextWord() {
  if (currentIndex.value < displayWords.value.length - 1) currentIndex.value++
}

function prevWord() {
  if (currentIndex.value > 0) currentIndex.value--
}

function jumpTo(word) {
  const idx = displayWords.value.findIndex(w => w.id === word.id)
  if (idx >= 0) currentIndex.value = idx
}

// Web Speech API — word pronunciation
function speakWord(word) {
  if (!window.speechSynthesis) return
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(word)
  utterance.lang = 'en-US'
  utterance.rate = 0.75
  utterance.pitch = 1
  window.speechSynthesis.speak(utterance)
}

onMounted(async () => {
  try {
    // Load all lessons first
    const lessonsRes = await getLessons({ limit: 144, offset: 0 })
    lessonList.value = lessonsRes.data.items
    const lessonIds = lessonsRes.data.items.map(l => l.id)

    // Load vocab for each lesson
    const vocabPromises = lessonIds.map(id => getLessonVocabulary(id))
    const vocabResults = await Promise.allSettled(vocabPromises)

    allWords.value = vocabResults
      .filter(r => r.status === 'fulfilled')
      .flatMap(r => r.value.data)

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

.flashcard-area {
  margin-bottom: 24px;
}

.speak-row {
  text-align: center;
  margin-top: 8px;
}

.speak-btn {
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 24px;
  font-size: 1rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.speak-btn:hover {
  background: #357abd;
}

.speak-btn:active {
  transform: scale(0.95);
}

.card-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  padding: 0 8px;
}

.nav-btn {
  padding: 8px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  color: #4a90d9;
}

.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.card-counter {
  font-size: 0.85rem;
  color: #888;
}

.lesson-filter {
  margin-bottom: 16px;
}

.lesson-filter select {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  background: white;
  outline: none;
}

.lesson-filter select:focus {
  border-color: #4a90d9;
}

.word-list-toggle {
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.word-list-toggle summary {
  cursor: pointer;
  font-weight: 600;
  color: #4a90d9;
  margin-bottom: 8px;
}

.word-table {
  margin-top: 8px;
}

.word-row {
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.word-row:hover {
  background: #f8f9fa;
}

.w-word {
  font-weight: 600;
  min-width: 80px;
}

.w-phonetic {
  color: #888;
  font-size: 0.85rem;
  min-width: 100px;
}

.w-meaning {
  flex: 1;
}

.speak-btn-small {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
  flex-shrink: 0;
}

.speak-btn-small:hover {
  background: #f0f7ff;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
