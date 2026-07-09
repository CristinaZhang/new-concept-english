<template>
  <div
    v-if="visible"
    class="word-popup"
    :style="{ top: popupTop + 'px', left: popupLeft + 'px' }"
  >
    <div v-if="loading" class="word-popup-loading">
      <span class="loading-dots">⏳ 查询中...</span>
    </div>

    <div v-else-if="error" class="word-popup-error">
      <p class="error-word">📖 {{ selectedText }}</p>
      <p class="error-msg">未找到释义，请手动输入</p>
      <div class="manual-form">
        <input v-model="manualWord" placeholder="单词" class="manual-input" />
        <input v-model="manualPhonetic" placeholder="音标（可选）" class="manual-input" />
        <input v-model="manualMeaning" placeholder="释义（可选）" class="manual-input" />
        <button class="action-btn add-btn" @click="onAddManual">加入生词本</button>
      </div>
      <button class="action-btn cancel-btn" @click="onCancel">取消</button>
    </div>

    <div v-else class="word-popup-content">
      <div class="word-header">
        <h3 class="dict-word">{{ dictResult.word }}</h3>
        <span class="dict-pos" v-if="dictResult.partOfSpeech">{{ dictResult.partOfSpeech }}</span>
      </div>
      <div class="dict-phonetic" v-if="dictResult.phonetic">🔊 {{ dictResult.phonetic }}</div>
      <div class="dict-definition">
        <span class="def-number">1.</span>
        <span class="def-text">{{ dictResult.meaning }}</span>
      </div>
      <div class="dict-example" v-if="dictResult.example">
        <em>"{{ dictResult.example }}"</em>
      </div>

      <!-- Editable fields -->
      <div class="edit-section">
        <input v-model="editWord" placeholder="单词" class="edit-input" />
        <input v-model="editPhonetic" placeholder="音标" class="edit-input" />
        <input v-model="editMeaning" placeholder="释义" class="edit-input" />
      </div>

      <div class="word-popup-actions">
        <button class="action-btn add-btn" @click="onAdd" :disabled="adding">
          {{ adding ? '添加中...' : '➕ 加入生词本' }}
        </button>
        <button class="action-btn cancel-btn" @click="onCancel">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { lookupWord } from '../utils/dictionary.js'

const props = defineProps({
  selectedText: { type: String, default: '' },
  popupTop: { type: Number, default: 0 },
  popupLeft: { type: Number, default: 0 },
})

const emit = defineEmits(['add', 'cancel'])

const visible = computed(() => !!props.selectedText)
const loading = ref(false)
const error = ref(false)
const adding = ref(false)

const dictResult = ref({ word: '', phonetic: '', meaning: '', partOfSpeech: '', example: '' })
const editWord = ref('')
const editPhonetic = ref('')
const editMeaning = ref('')

// Manual fallback fields
const manualWord = ref('')
const manualPhonetic = ref('')
const manualMeaning = ref('')

// When a new word is selected, reset and lookup
watch(() => props.selectedText, async (newWord) => {
  if (!newWord) return
  loading.value = true
  error.value = false
  editWord.value = ''
  editPhonetic.value = ''
  editMeaning.value = ''
  manualWord.value = newWord
  manualPhonetic.value = ''
  manualMeaning.value = ''

  try {
    const result = await lookupWord(newWord)
    if (result) {
      dictResult.value = result
      editWord.value = result.word
      editPhonetic.value = result.phonetic
      editMeaning.value = result.meaning
    } else {
      error.value = true
    }
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
})

async function onAdd() {
  if (adding.value) return
  adding.value = true
  try {
    await emit('add', {
      word: editWord.value || props.selectedText,
      phonetic: editPhonetic.value,
      meaning: editMeaning.value,
    })
  } finally {
    adding.value = false
  }
}

function onAddManual() {
  if (!manualWord.value.trim()) return
  emit('add', {
    word: manualWord.value.trim(),
    phonetic: manualPhonetic.value.trim(),
    meaning: manualMeaning.value.trim(),
  })
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
  border-radius: 14px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  padding: 16px;
  width: 300px;
  max-height: 80vh;
  overflow-y: auto;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Loading */
.word-popup-loading {
  text-align: center;
  padding: 16px 0;
  color: #999;
}

/* Error / Manual */
.word-popup-error {
  text-align: center;
}

.error-word {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 4px;
  color: #333;
}

.error-msg {
  color: #999;
  font-size: 0.85rem;
  margin: 0 0 12px;
}

.manual-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
}

.manual-input {
  padding: 8px 10px;
  border: 2px solid #eee;
  border-radius: 8px;
  font-size: 0.9rem;
}

.manual-input:focus {
  outline: none;
  border-color: #4a90d9;
}

/* Content */
.word-popup-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.word-header {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.dict-word {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #333;
}

.dict-pos {
  font-size: 0.75rem;
  color: #888;
  font-style: italic;
}

.dict-phonetic {
  font-size: 0.9rem;
  color: #666;
  font-family: 'Lucida Sans Unicode', sans-serif;
}

.dict-definition {
  display: flex;
  gap: 6px;
  font-size: 0.9rem;
  color: #444;
  line-height: 1.4;
}

.def-number {
  color: #4a90d9;
  font-weight: 600;
  flex-shrink: 0;
}

.def-text {
  flex: 1;
}

.dict-example {
  font-size: 0.8rem;
  color: #888;
  padding-left: 16px;
  border-left: 2px solid #e8f0fe;
  margin-top: 2px;
}

/* Editable fields */
.edit-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.edit-input {
  padding: 6px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 0.85rem;
  background: #fafafa;
}

.edit-input:focus {
  outline: none;
  border-color: #4a90d9;
  background: #f0f7ff;
}

/* Actions */
.word-popup-actions {
  display: flex;
  gap: 8px;
  margin-top: 4px;
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
