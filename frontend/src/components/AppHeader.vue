<template>
  <header class="app-header">
    <h1 class="logo" @click="$router.push('/lessons')">📖 新概念英语</h1>
  </header>
</template>

<script setup>
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
}

.logo {
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
}
</style>
