import axios from 'axios'

const api = axios.create({
  baseURL: '', // uses Vite dev proxy in dev, same-origin in prod
  timeout: 10000,
})

// ── Lessons ──────────────────────────────────────────────────────────

export function getLessons(params = {}) {
  return api.get('/v1/lessons', { params })
}

export function getLesson(id) {
  return api.get(`/v1/lessons/${id}`)
}

export function getLessonVocabulary(id) {
  return api.get(`/v1/lessons/${id}/vocabulary`)
}

export function getLessonGrammar(id) {
  return api.get(`/v1/lessons/${id}/grammar`)
}

// ── Vocabulary ───────────────────────────────────────────────────────

export function getVocabulary(id) {
  return api.get(`/v1/vocabulary/${id}`)
}

// ── Grammar & Exercises ──────────────────────────────────────────────

export function getGrammar(id) {
  return api.get(`/v1/grammar/${id}`)
}

export function getExercises(lessonId) {
  return api.get(`/v1/exercises/${lessonId}`)
}

export function submitExercise(id, answer) {
  return api.post(`/v1/exercises/${id}/submit`, { answer })
}

// ── Progress ─────────────────────────────────────────────────────────

export function getProgress() {
  return api.get('/v1/progress')
}

export function updateProgress(lessonId, data) {
  return api.post(`/v1/progress/lessons/${lessonId}`, data)
}

export function getProgressSummary() {
  return api.get('/v1/progress/summary')
}

export default api
