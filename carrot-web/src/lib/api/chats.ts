import apiClient from './axios'

export interface ChatRoomResponse {
  room_id: string
  post_id: number
  seller_email: string
  buyer_email: string
}

export interface ChatRoomListItem {
  room_id: string
  post_id: number
  post_thumbnail: string | null
  opponent_email: string
  seller_email: string
  buyer_email: string
  last_message: string
  last_sent_at: string
  unread_count: number
}

export interface MessageResponse {
  id: number
  room_id: string
  message: string
  sender_email: string
  sent_at: string
  is_read: boolean
}

export const chatsApi = {
  getUnreadCount: (): Promise<{ count: number }> =>
    apiClient.get<{ count: number }>('/api/v1/chats/unread-count').then((r) => r.data),

  markAsRead: (roomId: string): Promise<void> =>
    apiClient.patch(`/api/v1/chats/${roomId}/read`).then(() => undefined),

  getChatRooms: (): Promise<ChatRoomListItem[]> =>
    apiClient.get<ChatRoomListItem[]>('/api/v1/chats/').then((r) => r.data),

  createOrGetRoom: (postId: number): Promise<ChatRoomResponse> =>
    apiClient.post<ChatRoomResponse>('/api/v1/chats/', { post_id: postId }).then((r) => r.data),

  sendMessage: (roomId: string, message: string, postId: number): Promise<MessageResponse> =>
    apiClient
      .post<MessageResponse>(`/api/v1/chats/${roomId}/messages`, { message, post_id: postId })
      .then((r) => r.data),

  getMessages: (roomId: string, afterId?: number): Promise<MessageResponse[]> =>
    apiClient
      .get<MessageResponse[]>(`/api/v1/chats/${roomId}/messages`, {
        params: afterId ? { after: afterId } : undefined,
      })
      .then((r) => r.data),
}
