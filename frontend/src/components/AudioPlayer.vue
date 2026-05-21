<template>
  <div class="audio-player">
    <button class="play-btn" @click="togglePlay">
      {{ isPlaying ? '⏸' : '▶️' }}
    </button>
    <span class="label" v-if="label">{{ label }}</span>
    <audio
      ref="audioRef"
      :src="src"
      @ended="onEnded"
    ></audio>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  src: { type: String, default: '' },
  label: { type: String, default: '' },
})

const audioRef = ref(null)
const isPlaying = ref(false)

function togglePlay() {
  if (!audioRef.value || !props.src) return
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function onEnded() {
  isPlaying.value = false
}
</script>

<style scoped>
.audio-player {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.play-btn {
  background: #4a90d9;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.label {
  font-size: 0.85rem;
  color: #666;
}
</style>
