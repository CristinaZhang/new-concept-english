<template>
  <nav class="bottom-nav">
    <router-link to="/lessons" class="nav-item" active-class="active">
      <span class="nav-icon">📚</span>
      <span class="nav-label">课文</span>
    </router-link>
    <router-link to="/vocabulary" class="nav-item" active-class="active">
      <span class="nav-icon">📝</span>
      <span class="nav-label">词汇</span>
    </router-link>
    <router-link to="/spelling" class="nav-item" active-class="active">
      <span class="nav-icon">✏️</span>
      <span class="nav-label">拼写</span>
    </router-link>
    <router-link to="/grammar" class="nav-item" active-class="active">
      <span class="nav-icon">📐</span>
      <span class="nav-label">语法</span>
    </router-link>
  </nav>
</template>

<script setup>
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.08);
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: #999;
  font-size: 0.7rem;
  padding: 4px 12px;
  border-radius: 8px;
  transition: color 0.2s;
}

.nav-item.active {
  color: #4a90d9;
}

.nav-icon {
  font-size: 1.4rem;
  margin-bottom: 2px;
}
</style>
