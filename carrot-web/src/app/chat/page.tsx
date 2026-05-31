'use client'

import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { useQuery } from '@tanstack/react-query'
import { chatsApi, ChatRoomListItem } from '@/lib/api/chats'
import { usersApi } from '@/lib/api/users'
import { SiteHeader } from '@/components/layout/SiteHeader'

function formatElapsed(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '방금 전'
  if (minutes < 60) return `${minutes}분 전`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}시간 전`
  return `${Math.floor(hours / 24)}일 전`
}

function ChatListTile({
  room,
  onClick,
}: {
  room: ChatRoomListItem
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 border-b border-gray-100 text-left"
    >
      {/* 게시글 썸네일 */}
      <div className="w-12 h-12 rounded-lg bg-gray-100 shrink-0 overflow-hidden relative">
        {room.post_thumbnail ? (
          <Image
            src={room.post_thumbnail}
            alt=""
            fill
            className="object-cover"
            sizes="48px"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-xl">🖼️</div>
        )}
      </div>

      {/* 텍스트 영역 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <span className="font-medium text-sm text-gray-900 truncate">{room.opponent_email}</span>
          <span className="text-xs text-gray-400 shrink-0">{formatElapsed(room.last_sent_at)}</span>
        </div>
        <div className="flex items-center justify-between gap-2 mt-0.5">
          <span className="text-xs text-gray-500 truncate">{room.last_message}</span>
          {room.unread_count > 0 && (
            <span className="shrink-0 min-w-[20px] h-5 px-1.5 rounded-full text-white text-xs flex items-center justify-center" style={{ backgroundColor: '#FF7E36' }}>
              {room.unread_count > 99 ? '99+' : room.unread_count}
            </span>
          )}
        </div>
      </div>
    </button>
  )
}

export default function ChatListPage() {
  const router = useRouter()
  // 채팅 목록 진입 시 배지 즉시 갱신
  useQuery({
    queryKey: ['unread-count'],
    queryFn: () => chatsApi.getUnreadCount().catch(() => ({ count: 0 })),
    staleTime: 0,
  })

  const { data: me } = useQuery({
    queryKey: ['me'],
    queryFn: () => usersApi.getMe().catch(() => null),
    retry: false,
  })

  const { data: rooms = [], isLoading, isError } = useQuery<ChatRoomListItem[]>({
    queryKey: ['chats'],
    queryFn: () => chatsApi.getChatRooms(),
    enabled: !!me,
  })

  const handleRoomClick = (room: ChatRoomListItem) => {
    router.push(
      `/chat/${room.room_id}?postId=${room.post_id}&sellerEmail=${encodeURIComponent(room.seller_email)}&buyerEmail=${encodeURIComponent(room.buyer_email)}`
    )
  }

  if (!me) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 text-gray-400">
        <p>로그인이 필요합니다.</p>
        <button onClick={() => router.push('/auth/login')} className="text-sm underline" style={{ color: '#FF7E36' }}>
          로그인하기
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white max-w-2xl mx-auto">
      <SiteHeader />

      {isLoading && (
        <div className="p-8 text-center text-gray-400">불러오는 중...</div>
      )}
      {isError && (
        <div className="p-8 text-center text-red-400">채팅 목록을 불러올 수 없습니다.</div>
      )}
      {!isLoading && !isError && rooms.length === 0 && (
        <div className="p-8 text-center text-gray-400">채팅 내역이 없습니다.</div>
      )}

      <div>
        {rooms.map((room) => (
          <ChatListTile
            key={room.room_id}
            room={room}
            onClick={() => handleRoomClick(room)}
          />
        ))}
      </div>
    </div>
  )
}
