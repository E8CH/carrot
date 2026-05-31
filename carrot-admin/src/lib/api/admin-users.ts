import apiClient from './axios'

export interface AdminUserItem {
  email: string
  created_at: string
  manner_temp: number
  post_count: number
  is_active: boolean
}

export interface AdminUsersResponse {
  items: AdminUserItem[]
  total: number
}

export const adminUsersApi = {
  getUsers: (): Promise<AdminUsersResponse> =>
    apiClient.get<AdminUsersResponse>('/api/v1/admin/users').then((r) => r.data),

  updateStatus: (email: string, isActive: boolean): Promise<AdminUserItem> =>
    apiClient
      .patch<AdminUserItem>(`/api/v1/admin/users/${encodeURIComponent(email)}/status`, {
        is_active: isActive,
      })
      .then((r) => r.data),
}
