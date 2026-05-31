import apiClient from './axios'

export interface CreateReviewRequest {
  post_id: number
  is_positive: boolean
  tags: string[]
  comment: string | null
}

export interface ReviewResponse {
  id: number
  post_id: number
  writer_email: string
  target_email: string
  is_positive: boolean
  tags: string[]
  comment: string | null
  created_at: string
}

export const reviewsApi = {
  createReview: (data: CreateReviewRequest): Promise<ReviewResponse> =>
    apiClient.post<ReviewResponse>('/api/v1/reviews/', data).then((r) => r.data),
}
