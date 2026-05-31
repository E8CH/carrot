import apiClient from './axios'

export interface RegisterRequest {
  email: string
  password: string
  address: string
  phone: string
}

export interface UserInfo {
  id: number
  email: string
  address: string
  phone: string
  role: string
  manner_temp: number
  created_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export const authApi = {
  register: (data: RegisterRequest) =>
    apiClient.post<AuthResponse>('/api/v1/auth/register', data).then((r) => r.data),

  login: (data: { email: string; password: string }) =>
    apiClient.post<AuthResponse>('/api/v1/auth/login', data).then((r) => r.data),
}
