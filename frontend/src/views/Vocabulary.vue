<template>
  <div class="vocabulary-view">
    <h2 class="page-title">📝 词汇学习</h2>

    <!-- Flashcard mode -->
    <div class="flashcard-area" v-if="currentWord">
      <Flashcard :item="currentWord" />
      <div class="card-controls">
        <button class="nav-btn" @click="prevWord" :disabled="currentIndex === 0">上一词</button>
        <span class="card-counter">{{ currentIndex + 1 }} / {{ words.length }}</span>
        <button class="nav-btn" @click="nextWord" :disabled="currentIndex >= words.length - 1">下一词</button>
      </div>
    </div>

    <div v-else-if="loading" class="loading">加载中...</div>
    <div v-else class="empty">暂无词汇数据。</div>

    <!-- Word list toggle -->
    <details class="word-list-toggle">
      <summary>查看全部词汇列表</summary>
      <div class="word-table" v-if="words.length">
        <div class="word-row" v-for="w in words" :key="w.id" @click="jumpTo(w)">
          <span class="w-word">{{ w.word }}</span>
          <span class="w-phonetic">{{ w.phonetic }}</span>
          <span class="w-meaning">{{ w.meaning }}</span>
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
const loading = ref(true)
const currentIndex = ref(0)

const words = computed(() => allWords.value)
const currentWord = computed(() => words.value[currentIndex.value] || null)

function nextWord() {
  if (currentIndex.value < words.value.length - 1) currentIndex.value++
}

function prevWord() {
  if (currentIndex.value > 0) currentIndex.value--
}

function jumpTo(word) {
  const idx = words.value.findIndex(w => w.id === word.id)
  if (idx >= 0) currentIndex.value = idx
}

onMounted(async () => {
  try {
    // Load all lessons first
    const lessonsRes = await getLessons({ limit: 144, offset: 0 })
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

.word-list-toggle {
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
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

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
