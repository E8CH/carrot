import apiClient from './axios'

export interface PostListResponse {
  items: Array<{
    id: number
    title: string
    price: number | null
    is_free: boolean
    status: string
    thumbnail: string | null
    chat_count: number
    like_count: number
    created_at: string
  }>
  total: number
  page: number
  size: number
}

export interface UploadUrlResponse {
  upload_url: string
  file_path: string
}

export interface CreatePostRequest {
  title: string
  description: string
  price: number | null
  is_free: boolean
  trade_place: string | null
  photos: string[]
}

export interface PostDetailResponse {
  id: number
  seller_email: string
  title: string
  description: string
  price: number | null
  is_free: boolean
  status: string
  trade_place: string | null
  photos: string[]
  view_count: number
  created_at: string
  updated_at: string
  chat_count: number
  like_count: number
  manner_temp: number
  is_liked: boolean
}

export interface LikeResponse {
  is_liked: boolean
  like_count: number
}

export interface DraftResponse {
  id: number
  title: string
  description: string
  price: number | null
  is_free: boolean
  trade_place: string | null
  photos: string[]
  updated_at: string
}

export interface SaveDraftRequest {
  title: string
  description: string
  price: number | null
  is_free: boolean
  trade_place: string | null
  photos: string[]
}

export const postsApi = {
  getPosts: (page: number, size = 20) =>
    apiClient
      .get<PostListResponse>('/api/v1/posts/', { params: { page, size } })
      .then((r) => r.data),

  getUploadUrl: () =>
    apiClient.post<UploadUrlResponse>('/api/v1/posts/upload-url').then((r) => r.data),

  createPost: (data: CreatePostRequest) =>
    apiClient.post<PostDetailResponse>('/api/v1/posts/', data).then((r) => r.data),

  getDraft: (): Promise<DraftResponse | null> =>
    apiClient
      .get<DraftResponse>('/api/v1/posts/draft')
      .then((r) => r.data)
      .catch((err: { response?: { status?: number } }) => {
        if (err?.response?.status === 404) return null
        throw err
      }),

  saveDraft: (data: SaveDraftRequest) =>
    apiClient.post<DraftResponse>('/api/v1/posts/draft', data).then((r) => r.data),

  getPost: (id: number) =>
    apiClient.get<PostDetailResponse>(`/api/v1/posts/${id}`).then((r) => r.data),

  updatePost: (id: number, data: Partial<CreatePostRequest>) =>
    apiClient.patch<PostDetailResponse>(`/api/v1/posts/${id}`, data).then((r) => r.data),

  changeStatus: (id: number, status: string): Promise<PostDetailResponse> =>
    apiClient.patch<PostDetailResponse>(`/api/v1/posts/${id}/status`, { status }).then((r) => r.data),

  getPostBuyers: (id: number): Promise<{ buyers: Array<{ buyer_email: string }> }> =>
    apiClient.get(`/api/v1/posts/${id}/buyers`).then((r) => r.data),

  completePost: (id: number, buyerEmail: string): Promise<PostDetailResponse> =>
    apiClient
      .patch<PostDetailResponse>(`/api/v1/posts/${id}/complete`, { buyer_email: buyerEmail })
      .then((r) => r.data),

  deletePost: (id: number) =>
    apiClient.delete(`/api/v1/posts/${id}`).then(() => undefined),

  toggleLike: (id: number): Promise<LikeResponse> =>
    apiClient.post<LikeResponse>(`/api/v1/posts/${id}/like`).then((r) => r.data),
}
