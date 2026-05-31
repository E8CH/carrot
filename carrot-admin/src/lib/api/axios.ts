import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// 요청 인터셉터: 관리자 JWT 자동 주입 (AR-8)
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// 응답 인터셉터: 401/403 → 로그인 리다이렉트
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      (error.response?.status === 401 || error.response?.status === 403) &&
      typeof window !== 'undefined'
    ) {
      localStorage.removeItem('admin_token')
      window.location.href = '/auth/login'
      return new Promise(() => {})
    }
    return Promise.reject(error)
  }
)

export default apiClient
