import apiClient from './axios'
import type { UserInfo } from './auth'

export interface MyPostItem {
  id: number
  title: string
  price: number | null
  is_free: boolean
  status: string
  thumbnail: string | null
  chat_count: number
  like_count: number
  created_at: string
}

export interface MyPostsResponse {
  items: MyPostItem[]
  total: number
}

export interface PurchaseItem {
  id: number
  title: string
  thumbnail: string | null
  price: number | null
  is_free: boolean
  updated_at: string
}

export interface PurchasesResponse {
  items: PurchaseItem[]
  total: number
}

export const usersApi = {
  getMe: () =>
    apiClient.get<UserInfo>('/api/v1/users/me').then((r) => r.data),

  getMyPosts: (status?: string): Promise<MyPostsResponse> =>
    apiClient
      .get<MyPostsResponse>('/api/v1/users/me/posts', {
        params: status ? { status } : {},
      })
      .then((r) => r.data),

  getMyPurchases: (): Promise<PurchasesResponse> =>
    apiClient.get<PurchasesResponse>('/api/v1/users/me/purchases').then((r) => r.data),

  getMyLikes: (): Promise<MyPostsResponse> =>
    apiClient.get<MyPostsResponse>('/api/v1/users/me/likes').then((r) => r.data),
}
