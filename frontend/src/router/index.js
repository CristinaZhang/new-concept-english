import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/lessons',
  },
  {
    path: '/lessons',
    name: 'LessonList',
    component: () => import('../views/LessonList.vue'),
  },
  {
    path: '/lessons/:id',
    name: 'LessonDetail',
    component: () => import('../views/LessonDetail.vue'),
  },
  {
    path: '/vocabulary',
    name: 'Vocabulary',
    component: () => import('../views/Vocabulary.vue'),
  },
  {
    path: '/spelling',
    name: 'SpellingPractice',
    component: () => import('../views/SpellingPractice.vue'),
  },
  {
    path: '/grammar',
    name: 'Grammar',
    component: () => import('../views/Grammar.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
