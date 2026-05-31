import apiClient from './axios'

export interface AdminChatRoomItem {
  room_id: string
  seller_email: string
  buyer_email: string
  post_title: string
  message_count: number
  last_message_at: string
}

export interface AdminChatRoomsResponse {
  items: AdminChatRoomItem[]
  total: number
}

export interface AdminChatMessageItem {
  id: number
  sender_email: string
  message: string
  sent_at: string
}

export interface AdminChatMessagesResponse {
  room_id: string
  items: AdminChatMessageItem[]
}

export const adminChatsApi = {
  getChats: (): Promise<AdminChatRoomsResponse> =>
    apiClient.get<AdminChatRoomsResponse>('/api/v1/admin/chats').then((r) => r.data),

  getMessages: (roomId: string): Promise<AdminChatMessagesResponse> =>
    apiClient
      .get<AdminChatMessagesResponse>(`/api/v1/admin/chats/${roomId}/messages`)
      .then((r) => r.data),
}
