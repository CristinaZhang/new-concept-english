<template>
  <div class="score-display">
    <div class="score-circle" :class="scoreClass">
      <span class="score-value">{{ score }}</span>
      <span class="score-total">/ {{ total }}</span>
    </div>
    <div class="score-label">{{ label }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  score: { type: Number, default: 0 },
  total: { type: Number, default: 10 },
  label: { type: String, default: '得分' },
})

const scoreClass = computed(() => {
  const pct = props.total > 0 ? (props.score / props.total) * 100 : 0
  if (pct >= 80) return 'great'
  if (pct >= 60) return 'good'
  return 'needs-work'
})
</script>

<style scoped>
.score-display {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.score-circle.great {
  background: #e8f5e9;
  color: #2e7d32;
}

.score-circle.good {
  background: #fff3e0;
  color: #ef6c00;
}

.score-circle.needs-work {
  background: #fce4ec;
  color: #c62828;
}

.score-value {
  font-size: 1.8rem;
}

.score-total {
  font-size: 0.75rem;
  opacity: 0.7;
}

.score-label {
  font-size: 0.85rem;
  color: #666;
  margin-top: 8px;
}
</style>
