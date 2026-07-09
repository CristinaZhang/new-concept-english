import axios from 'axios'
import { getUserId } from '../utils/user.js'

const api = axios.create({
  baseURL: '', // uses Vite dev proxy in dev, same-origin in prod
  timeout: 10000,
})

// ── Lessons ──────────────────────────────────────────────────────────

export function getLessons(params = {}) {
  return api.get('/v1/lessons', { params: { user_id: getUserId(), ...params } })
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
  return api.get('/v1/progress', { params: { user_id: getUserId() } })
}

export function updateProgress(lessonId, data) {
  return api.post(`/v1/progress/lessons/${lessonId}`, data, { params: { user_id: getUserId() } })
}

export function getProgressSummary() {
  return api.get('/v1/progress/summary', { params: { user_id: getUserId() } })
}

// ── Users ────────────────────────────────────────────────────────────

export function getUsers() {
  return api.get('/v1/users')
}

export function createUser(data) {
  return api.post('/v1/users', data)
}

export function deleteUser(userId) {
  return api.delete(`/v1/users/${userId}`)
}

// ── Personal Vocabulary ─────────────────────────────────────────────

export function getPersonalVocab(params = {}) {
  return api.get('/v1/personal-vocab', { params: { user_id: getUserId(), ...params } })
}

export function addPersonalVocab(data) {
  return api.post('/v1/personal-vocab', data, { params: { user_id: getUserId() } })
}

export function deletePersonalVocab(id) {
  return api.delete(`/v1/personal-vocab/${id}`, { params: { user_id: getUserId() } })
}

export default api
