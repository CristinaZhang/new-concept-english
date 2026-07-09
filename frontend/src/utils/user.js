/**
 * User identity management for multi-user NCE learning.
 *
 * Users are identified by a short code (e.g. "abc123") passed via URL query
 * param `?user=abc123`. Once set, the ID is persisted in localStorage so
 * subsequent visits don't need the URL param.
 *
 * If no user is set, all API calls fall back to the "default" profile.
 */

const STORAGE_KEY = 'nce_user_id'

/**
 * Get current user ID from URL param or localStorage.
 * If URL has ?user=xxx, it overrides localStorage and persists there.
 */
export function getUserId() {
  const params = new URLSearchParams(window.location.search)
  const urlUser = params.get('user')
  if (urlUser && urlUser.trim()) {
    const id = urlUser.trim()
    localStorage.setItem(STORAGE_KEY, id)
    return id
  }
  return localStorage.getItem(STORAGE_KEY) || 'default'
}

/**
 * Switch to a different user ID.
 */
export function setUserId(userId) {
  if (userId && userId.trim()) {
    localStorage.setItem(STORAGE_KEY, userId.trim())
  } else {
    localStorage.removeItem(STORAGE_KEY)
  }
}

/**
 * Get the display name for the current user.
 */
export function getUserDisplayName() {
  const id = getUserId()
  if (id === 'default') return '默认用户'
  return id
}

/**
 * Check if a user is currently selected (not "default").
 */
export function hasUser() {
  return localStorage.getItem(STORAGE_KEY) !== null
}
