'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { adminChatsApi, AdminChatRoomItem } from '@/lib/api/admin-chats'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function ChatsPage() {
  const [selectedRoom, setSelectedRoom] = useState<AdminChatRoomItem | null>(null)

  const { data: roomsData, isLoading: roomsLoading, isError: roomsError } = useQuery({
    queryKey: ['admin', 'chats'],
    queryFn: adminChatsApi.getChats,
  })

  const { data: messagesData, isLoading: messagesLoading } = useQuery({
    queryKey: ['admin', 'chats', selectedRoom?.room_id, 'messages'],
    queryFn: () => adminChatsApi.getMessages(selectedRoom!.room_id),
    enabled: !!selectedRoom,
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">채팅 관리</h1>
        {roomsData && (
          <span className="text-sm text-gray-500">전체 {roomsData.total}개</span>
        )}
      </div>

      {roomsLoading && (
        <div className="py-20 text-center text-gray-400">불러오는 중...</div>
      )}
      {roomsError && (
        <div className="py-20 text-center text-red-500">
          채팅 목록을 불러올 수 없습니다.
        </div>
      )}

      {roomsData && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">채팅방 ID</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">판매자</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">구매자</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">게시글</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">메시지</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">마지막 시간</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">열람</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {roomsData.items.map((room) => (
                <tr
                  key={room.room_id}
                  className={`hover:bg-gray-50 transition-colors ${
                    selectedRoom?.room_id === room.room_id ? 'bg-orange-50' : ''
                  }`}
                >
                  <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                    {room.room_id.slice(0, 8)}…
                  </td>
                  <td className="px-4 py-3 text-gray-600">{room.seller_email}</td>
                  <td className="px-4 py-3 text-gray-600">{room.buyer_email}</td>
                  <td className="px-4 py-3 text-gray-800 max-w-[160px] truncate">
                    {room.post_title}
                  </td>
                  <td className="px-4 py-3 text-center text-gray-600">
                    {room.message_count}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {formatDate(room.last_message_at)}{' '}
                    {formatTime(room.last_message_at)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() =>
                        setSelectedRoom(
                          selectedRoom?.room_id === room.room_id ? null : room
                        )
                      }
                      className={`px-3 py-1 text-xs rounded-lg border transition-colors ${
                        selectedRoom?.room_id === room.room_id
                          ? 'bg-orange-500 text-white border-orange-500'
                          : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {selectedRoom?.room_id === room.room_id ? '닫기' : '보기'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {roomsData.items.length === 0 && (
            <div className="py-16 text-center text-gray-400">채팅 내역이 없습니다.</div>
          )}
        </div>
      )}

      {selectedRoom && (
        <div className="bg-white rounded-xl shadow-sm p-4 space-y-3">
          <div className="border-b border-gray-100 pb-3">
            <h2 className="text-sm font-semibold text-gray-700">
              메시지 내역 — {selectedRoom.seller_email} ↔ {selectedRoom.buyer_email}
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">{selectedRoom.post_title}</p>
          </div>

          {messagesLoading && (
            <div className="py-8 text-center text-gray-400 text-sm">
              메시지 로딩 중...
            </div>
          )}

          {messagesData && (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {messagesData.items.map((msg) => {
                const isSeller =
                  msg.sender_email.toLowerCase() === selectedRoom.seller_email.toLowerCase()
                return (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${isSeller ? 'items-end' : 'items-start'}`}
                  >
                    <span className="text-xs text-gray-400 mb-0.5">
                      {msg.sender_email} · {formatTime(msg.sent_at)}
                    </span>
                    <div
                      className={`px-3 py-2 rounded-xl text-sm max-w-[70%] ${
                        isSeller
                          ? 'bg-orange-500 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {msg.message}
                    </div>
                  </div>
                )
              })}
              {messagesData.items.length === 0 && (
                <div className="py-8 text-center text-gray-400 text-sm">
                  메시지가 없습니다.
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
