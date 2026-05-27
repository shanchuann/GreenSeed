import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import api from '@/api'

export interface WorkExperience {
  company: string
  position: string
  start_date: string
  end_date?: string
  description?: string
}

export interface ProjectExperience {
  project_name: string
  project_link?: string
  start_date: string
  end_date?: string
  tech_stack?: string[]
  description?: string
  results?: string
}

export interface User {
  id: string
  email: string
  name: string
  role: 'seeker' | 'recruiter' | 'admin'
  phone?: string
  avatar_url?: string
  bio?: string
  skills?: string[]
  education?: string
  desired_position?: string[]
  desired_salary_min?: number
  desired_salary_max?: number
  desired_city?: string
  available_date?: string
  work_experience?: WorkExperience[]
  project_experience?: ProjectExperience[]
  resume_url?: string
  gender?: string
  job_status?: string
  birth_year?: number
  birth_month?: number
  wechat?: string
  created_at?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user  = ref<User | null>(null)
  const token = ref<string | null>(null)

  const isLoggedIn  = computed(() => !!token.value)
  const isSeeker    = computed(() => user.value?.role === 'seeker')
  const isRecruiter = computed(() => user.value?.role === 'recruiter')
  const isAdmin     = computed(() => user.value?.role === 'admin')
  const isRestored  = ref(false)

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
    return (_restorePromise = fetchMe().finally(() => { isRestored.value = true }))
  }

  async function fetchMe() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch (err: any) {
      if (err?.response?.status !== 401) {
        logout()
      }
      // 401 handled by api interceptor (refresh → retry or redirect)
    }
  }

  async function login(email: string, password: string) {
    const res = await axios.post('/api/auth/login', { email, password })
    token.value = res.data.access_token
    user.value  = res.data.user
    localStorage.setItem('gs-token', token.value!)
    if (res.data.refresh_token) {
      localStorage.setItem('gs-refresh-token', res.data.refresh_token)
    }
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
      if (res.data.refresh_token) {
        localStorage.setItem('gs-refresh-token', res.data.refresh_token)
      }
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
    }
  }

  function logout() {
    user.value       = null
    token.value      = null
    isRestored.value = false
    _restorePromise  = null
    localStorage.removeItem('gs-token')
    localStorage.removeItem('gs-refresh-token')
    delete axios.defaults.headers.common['Authorization']
  }

  return { user, token, isLoggedIn, isSeeker, isRecruiter, isAdmin, isRestored, restore, login, register, logout, fetchMe }
})
