<template>
  <div
    v-if="visible"
    class="word-popup"
    :style="{ top: popupTop + 'px', left: popupLeft + 'px' }"
  >
    <div class="word-popup-header">
      <span class="selected-word">{{ selectedText }}</span>
    </div>
    <div class="word-popup-actions">
      <button class="action-btn add-btn" @click="onAdd" :disabled="adding">
        {{ adding ? '添加中...' : '➕ 加入生词本' }}
      </button>
      <button class="action-btn cancel-btn" @click="onCancel">取消</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  selectedText: { type: String, default: '' },
  popupTop: { type: Number, default: 0 },
  popupLeft: { type: Number, default: 0 },
})

const emit = defineEmits(['add', 'cancel'])
const adding = ref(false)

const visible = computed(() => !!props.selectedText)

async function onAdd() {
  if (adding.value) return
  adding.value = true
  try {
    await emit('add', props.selectedText)
  } finally {
    adding.value = false
  }
}

function onCancel() {
  emit('cancel')
}
</script>

<style scoped>
.word-popup {
  position: fixed;
  z-index: 300;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 12px;
  min-width: 200px;
  max-width: 280px;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.word-popup-header {
  margin-bottom: 10px;
}

.selected-word {
  display: block;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  word-break: break-word;
}

.word-popup-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  padding: 8px;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.add-btn {
  background: #4a90d9;
  color: white;
}

.add-btn:hover:not(:disabled) {
  background: #357abd;
}

.add-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}
</style>
