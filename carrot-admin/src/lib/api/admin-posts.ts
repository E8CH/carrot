import apiClient from './axios'

export interface AdminPostItem {
  id: number
  title: string
  seller_email: string
  price: number | null
  is_free: boolean
  status: string
  created_at: string
}

export interface AdminPostsResponse {
  items: AdminPostItem[]
  total: number
}

export const adminPostsApi = {
  getPosts: (status?: string): Promise<AdminPostsResponse> =>
    apiClient
      .get<AdminPostsResponse>('/api/v1/admin/posts', {
        params: status ? { status } : undefined,
      })
      .then((r) => r.data),

  deletePost: (postId: number): Promise<void> =>
    apiClient.delete(`/api/v1/admin/posts/${postId}`).then(() => {}),
}
