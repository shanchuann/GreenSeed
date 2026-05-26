import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export interface User {
  id: string
  email: string
  name: string
  role: 'seeker' | 'recruiter' | 'admin'
  avatar_url?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isLoggedIn  = computed(() => !!token.value)
  const isSeeker    = computed(() => user.value?.role === 'seeker')
  const isRecruiter = computed(() => user.value?.role === 'recruiter')
  const isAdmin     = computed(() => user.value?.role === 'admin')
  const isRestored  = ref(false)

  // 幂等：多次调用共享同一个 Promise，避免重复请求
  let _restorePromise: Promise<void> | null = null

  function restore(): Promise<void> {
    if (_restorePromise) return _restorePromise
    const saved = localStorage.getItem('gs-token')
    if (!saved) {
      isRestored.value = true
      return (_restorePromise = Promise.resolve())
    }
    token.value = saved
    axios.defaults.headers.common['Authorization'] = `Bearer ${saved}`
    // .finally 在 Promise resolve 前运行，保证 isRestored 先于 await 返回处被设置
    return (_restorePromise = fetchMe().finally(() => { isRestored.value = true }))
  }

  async function fetchMe() {
    try {
      const res = await axios.get('/api/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  async function login(email: string, password: string) {
    const res = await axios.post('/api/auth/login', { email, password })
    token.value = res.data.access_token
    user.value  = res.data.user
    localStorage.setItem('gs-token', token.value!)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  async function register(payload: {
    email: string
    password: string
    name: string
    role: 'seeker' | 'recruiter'
  }) {
    const res = await axios.post('/api/auth/register', payload)
    user.value = res.data.user
    if (res.data.access_token) {
      token.value = res.data.access_token
      localStorage.setItem('gs-token', token.value!)
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
    // empty token means email confirmation is required — caller should handle redirect
  }

  function logout() {
    user.value       = null
    token.value      = null
    isRestored.value = false
    _restorePromise  = null
    localStorage.removeItem('gs-token')
    delete axios.defaults.headers.common['Authorization']
  }

  return { user, token, isLoggedIn, isSeeker, isRecruiter, isAdmin, isRestored, restore, login, register, logout, fetchMe }
})
