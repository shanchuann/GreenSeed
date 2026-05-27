import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('gs-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRefreshing = false
let refreshQueue: Array<(token: string) => void> = []

function drainQueue(token: string) {
  refreshQueue.forEach(cb => cb(token))
  refreshQueue = []
}

function redirectLogin() {
  localStorage.removeItem('gs-token')
  localStorage.removeItem('gs-refresh-token')
  window.location.href = '/login'
}

api.interceptors.response.use(
  res => res,
  async (err) => {
    const original = err.config
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }

    const refreshToken = localStorage.getItem('gs-refresh-token')
    if (!refreshToken) {
      redirectLogin()
      return Promise.reject(err)
    }

    if (isRefreshing) {
      return new Promise(resolve => {
        refreshQueue.push(token => {
          original.headers.Authorization = `Bearer ${token}`
          resolve(api(original))
        })
      })
    }

    original._retry = true
    isRefreshing = true
    try {
      const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
      const { access_token, refresh_token: newRefresh } = data
      localStorage.setItem('gs-token', access_token)
      if (newRefresh) localStorage.setItem('gs-refresh-token', newRefresh)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      drainQueue(access_token)
      original.headers.Authorization = `Bearer ${access_token}`
      return api(original)
    } catch {
      redirectLogin()
      return Promise.reject(err)
    } finally {
      isRefreshing = false
    }
  },
)

export default api
