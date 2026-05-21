<template>
  <div class="flashcard" @click="flipped = !flipped">
    <div class="card-inner" :class="{ 'is-flipped': flipped }">
      <div class="card-front">
        <div class="word">{{ item.word }}</div>
        <div class="phonetic" v-if="item.phonetic">{{ item.phonetic }}</div>
        <div class="hint">点击查看释义</div>
      </div>
      <div class="card-back">
        <div class="meaning">{{ item.meaning }}</div>
        <div class="example" v-if="item.example_sentence">{{ item.example_sentence }}</div>
        <div class="hint">点击返回</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
})

const flipped = ref(false)
</script>

<style scoped>
.flashcard {
  perspective: 800px;
  cursor: pointer;
  margin: 16px auto;
  max-width: 360px;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 200px;
  transition: transform 0.5s;
  transform-style: preserve-3d;
}

.card-inner.is-flipped {
  transform: rotateY(180deg);
}

.card-front, .card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
}

.card-front {
  background: white;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.card-back {
  background: #4a90d9;
  color: white;
  transform: rotateY(180deg);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.word {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.phonetic {
  font-size: 1rem;
  color: #888;
  margin-bottom: 12px;
}

.meaning {
  font-size: 1.3rem;
  margin-bottom: 12px;
}

.example {
  font-size: 0.9rem;
  opacity: 0.85;
}

.hint {
  font-size: 0.75rem;
  color: #aaa;
  margin-top: 12px;
}

.card-back .hint {
  color: rgba(255,255,255,0.7);
}
</style>
