import apiClient from './axios'

export interface AdminUser {
  id: number
  email: string
  role: string
  manner_temp: number
  created_at: string
}

export interface AdminAuthResponse {
  access_token: string
  token_type: string
  user: AdminUser
}

export const adminAuthApi = {
  login: (email: string, password: string): Promise<AdminAuthResponse> =>
    apiClient
      .post<AdminAuthResponse>('/api/v1/admin/login', { email, password })
      .then((r) => r.data),

  register: (email: string, password: string): Promise<AdminAuthResponse> =>
    apiClient
      .post<AdminAuthResponse>('/api/v1/admin/register', { email, password })
      .then((r) => r.data),
}
