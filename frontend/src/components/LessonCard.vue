<template>
  <div class="lesson-card" @click="$router.push(`/lessons/${lesson.id}`)">
    <div class="card-left">
      <span class="lesson-num">L{{ lesson.lesson_number }}</span>
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
})
</script>

<style scoped>
.lesson-card {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  margin-bottom: 10px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}

.lesson-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-left {
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
}

.card-body {
  flex: 1;
}

.card-title {
  font-size: 1rem;
  color: #333;
  margin-bottom: 2px;
}

.card-level {
  font-size: 0.75rem;
  color: #999;
}

.card-right .arrow {
  font-size: 1.5rem;
  color: #ccc;
}
</style>
