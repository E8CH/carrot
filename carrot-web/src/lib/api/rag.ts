import apiClient from './axios'

export interface ChatResponse {
  answer: string
  sources: { source_type: string; source_id: string; content: string }[]
}

export const ragApi = {
  chat: async (message: string): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>('/api/v1/rag/chat', { message })
    return data
  },
}
