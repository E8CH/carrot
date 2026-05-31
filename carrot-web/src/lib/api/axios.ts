import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// 요청 인터셉터: JWT 자동 주입 (AR-8)
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// 응답 인터셉터: 401 → 로그인 리다이렉트 (FR-3)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      localStorage.removeItem('token')
      window.location.href = '/auth/login'
      // 리다이렉트 중 호출자의 catch 핸들러가 실행되지 않도록 pending promise 반환
      return new Promise(() => {})
    }
    return Promise.reject(error)
  }
)

export default apiClient
