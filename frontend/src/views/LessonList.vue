<template>
  <div class="lesson-list">
    <h2 class="page-title">📚 新概念英语第一册</h2>

    <!-- Progress summary -->
    <div class="summary-bar" v-if="summary.total_lessons > 0">
      <div class="summary-item">
        <span class="summary-value">{{ summary.completed_lessons }}</span>
        <span class="summary-label">已学</span>
      </div>
      <div class="summary-item">
        <span class="summary-value">{{ summary.total_lessons }}</span>
        <span class="summary-label">总课文</span>
      </div>
      <div class="summary-item">
        <span class="summary-value">{{ summary.completion_rate }}%</span>
        <span class="summary-label">完成率</span>
      </div>
    </div>

    <!-- Lesson list -->
    <div class="cards" v-if="lessons.length">
      <LessonCard v-for="lesson in lessons" :key="lesson.id" :lesson="lesson" />
    </div>

    <div v-else-if="loading" class="loading">加载中...</div>
    <div v-else class="empty">暂无课文数据，请先运行种子数据导入。</div>

    <!-- Load more -->
    <button
      v-if="hasMore"
      class="load-more"
      @click="loadMore"
      :disabled="loading"
    >
      {{ loading ? '加载中...' : '加载更多' }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getLessons, getProgressSummary } from '../api/index.js'
import LessonCard from '../components/LessonCard.vue'

const lessons = ref([])
const loading = ref(false)
const offset = ref(0)
const total = ref(0)
const limit = ref(20)
const summary = ref({ total_lessons: 0, completed_lessons: 0, completion_rate: 0 })

const hasMore = ref(true)

async function loadLessons() {
  loading.value = true
  try {
    const res = await getLessons({ limit: limit.value, offset: offset.value })
    lessons.value = [...lessons.value, ...res.data.items]
    total.value = res.data.total
    offset.value += limit.value
    hasMore.value = offset.value < total.value
  } catch (e) {
    console.error('Failed to load lessons:', e)
  } finally {
    loading.value = false
  }
}

async function loadSummary() {
  try {
    const res = await getProgressSummary()
    summary.value = res.data
  } catch (e) {
    console.error('Failed to load summary:', e)
  }
}

function loadMore() {
  loadLessons()
}

onMounted(() => {
  loadLessons()
  loadSummary()
})
</script>

<style scoped>
.page-title {
  font-size: 1.4rem;
  margin-bottom: 16px;
  color: #333;
}

.summary-bar {
  display: flex;
  justify-content: space-around;
  background: linear-gradient(135deg, #4a90d9, #357abd);
  color: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
}

.summary-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
}

.summary-label {
  font-size: 0.75rem;
  opacity: 0.85;
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

.load-more {
  display: block;
  width: 100%;
  padding: 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.95rem;
  color: #4a90d9;
  cursor: pointer;
  margin-top: 12px;
}

.load-more:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
