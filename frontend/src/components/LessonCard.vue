<template>
  <div class="lesson-card" @click="$emit('click')">
    <div class="card-left">
      <span class="lesson-num">L{{ lesson.lesson_number }}</span>
      <span v-if="badge" class="badge" :style="{ background: badgeColor + '20', color: badgeColor }">{{ badge }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ lesson.title }}</h3>
      <p class="card-level">{{ lesson.level }}</p>
    </div>
    <div class="card-right">
      <span class="arrow">›</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  lesson: { type: Object, required: true },
  badge: { type: String, default: '' },
  badgeColor: { type: String, default: '#4a90d9' },
})
</script>

<style scoped>
.lesson-card {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 10px 14px;
  margin: 2px 2px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.lesson-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.card-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-right: 12px;
}

.lesson-num {
  display: inline-block;
  background: #e8f0fe;
  color: #4a90d9;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 4px 10px;
  border-radius: 8px;
  text-align: center;
}

.badge {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 6px;
  text-align: center;
}

.card-body {
  flex: 1;
}

.card-title {
  font-size: 0.95rem;
  color: #333;
  margin-bottom: 2px;
}

.card-level {
  font-size: 0.7rem;
  color: #999;
}

.card-right .arrow {
  font-size: 1.5rem;
  color: #ccc;
}
</style>
