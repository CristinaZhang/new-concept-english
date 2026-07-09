<template>
  <header class="app-header">
    <h1 class="logo" @click="$router.push('/lessons')">📖 新概念英语</h1>
    <div class="user-section">
      <div class="user-badge" @click="showUserDialog = true">
        <span class="user-icon">👤</span>
        <span class="user-name">{{ displayName }}</span>
      </div>
    </div>

    <!-- User switch dialog -->
    <div v-if="showUserDialog" class="modal-overlay" @click.self="showUserDialog = false">
      <div class="modal">
        <h3>切换用户 / 新用户</h3>
        <div class="user-list" v-if="users.length > 0">
          <button
            v-for="u in users"
            :key="u.user_id"
            class="user-option"
            :class="{ active: u.user_id === currentUserId }"
            @click="selectUser(u.user_id)"
          >
            <span class="user-option-icon">👤</span>
            <span class="user-option-name">{{ u.name || u.user_id }}</span>
            <span class="user-option-id">{{ u.user_id }}</span>
          </button>
        </div>
        <p v-else class="no-users">暂无已注册用户</p>

        <div class="new-user-section">
          <h4>新用户</h4>
          <div class="new-user-form">
            <input
              v-model="newUserId"
              placeholder="用户ID（如 abc123）"
              class="user-input"
              maxlength="20"
            />
            <button class="create-btn" @click="createUser" :disabled="!newUserId.trim()">
              创建
            </button>
          </div>
          <div v-if="createError" class="error">{{ createError }}</div>
        </div>

        <button class="close-btn" @click="showUserDialog = false">关闭</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getUserId, setUserId, getUserDisplayName } from '../utils/user.js'
import { getUsers } from '../api/index.js'

const showUserDialog = ref(false)
const users = ref([])
const newUserId = ref('')
const createError = ref('')

const currentUserId = computed(() => getUserId())
const displayName = computed(() => {
  const id = getUserId()
  const user = users.value.find(u => u.user_id === id)
  return user ? `${user.name} (${user.user_id})` : id
})

async function loadUsers() {
  try {
    const res = await getUsers()
    users.value = res.data
  } catch (e) {
    console.error('Failed to load users:', e)
  }
}

function selectUser(userId) {
  setUserId(userId)
  showUserDialog.value = false
  window.location.reload() // reload to apply new user's data
}

async function createUser() {
  createError.value = ''
  if (!newUserId.value.trim()) return
  try {
    const { default: axios } = await import('axios')
    const res = await axios.post('/v1/users', {
      user_id: newUserId.value.trim(),
      name: newUserId.value.trim()
    })
    users.value.push(res.data)
    selectUser(res.data.user_id)
    newUserId.value = ''
  } catch (e) {
    createError.value = e.response?.data?.detail || '创建失败，请重试'
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.app-header {
  background: #4a90d9;
  color: white;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 20px;
  padding: 4px 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.user-badge:hover {
  background: rgba(255,255,255,0.3);
}

.user-icon {
  font-size: 1rem;
}

.user-name {
  font-size: 0.85rem;
  font-weight: 500;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

.modal h3 {
  margin: 0 0 16px;
  color: #333;
  font-size: 1.1rem;
}

.modal h4 {
  margin: 16px 0 8px;
  color: #555;
  font-size: 0.95rem;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 2px solid #eee;
  border-radius: 10px;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.2s;
}

.user-option:hover {
  background: #e8f0fe;
  border-color: #4a90d9;
}

.user-option.active {
  background: #e8f0fe;
  border-color: #4a90d9;
}

.user-option-icon {
  font-size: 1.2rem;
}

.user-option-name {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.user-option-id {
  font-size: 0.75rem;
  color: #999;
  font-family: monospace;
}

.no-users {
  color: #999;
  text-align: center;
  padding: 12px;
  font-size: 0.9rem;
}

.new-user-section {
  margin-top: 8px;
}

.new-user-form {
  display: flex;
  gap: 8px;
}

.user-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
}

.user-input:focus {
  outline: none;
  border-color: #4a90d9;
}

.create-btn {
  padding: 8px 16px;
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.create-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 8px;
}

.close-btn {
  margin-top: 16px;
  width: 100%;
  padding: 10px;
  background: #f0f0f0;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}

.close-btn:hover {
  background: #e0e0e0;
}
</style>
