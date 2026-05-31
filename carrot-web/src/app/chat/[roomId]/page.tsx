'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { chatsApi, MessageResponse } from '@/lib/api/chats'
import { usersApi } from '@/lib/api/users'

interface OptimisticMessage {
  tempId: number
  message: string
  sender_email: string
  sent_at: string
  pending: boolean
  error: boolean
}

function ChatBubble({
  message,
  isMine,
  pending,
  error,
}: {
  message: string
  isMine: boolean
  pending?: boolean
  error?: boolean
}) {
  return (
    <div className={`flex ${isMine ? 'justify-end' : 'justify-start'} px-3 py-1`}>
      <div
        className={`max-w-[72%] px-4 py-2.5 rounded-2xl text-sm ${
          isMine
            ? 'text-white rounded-br-sm'
            : 'text-gray-800 bg-gray-100 rounded-bl-sm'
        }`}
        style={isMine ? { backgroundColor: '#FF7E36' } : undefined}
      >
        <span>{message}</span>
        {pending && <span className="ml-1.5 text-xs opacity-70">⏳</span>}
        {error && <span className="ml-1.5 text-xs text-red-200">❌</span>}
      </div>
    </div>
  )
}

export default function ChatRoomPage() {
  const { roomId } = useParams<{ roomId: string }>()
  const searchParams = useSearchParams()
  const router = useRouter()

  const postId = Number(searchParams.get('postId'))
  const sellerEmail = searchParams.get('sellerEmail') ?? ''

  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [optimisticMessages, setOptimisticMessages] = useState<OptimisticMessage[]>([])
  const [allMessages, setAllMessages] = useState<MessageResponse[]>([])
  const lastIdRef = useRef<number | undefined>(undefined)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const { data: me } = useQuery({
    queryKey: ['me'],
    queryFn: () => usersApi.getMe().catch(() => null),
    retry: false,
  })
  const myEmail = me?.email ?? ''

  // 채팅방 진입 시 읽음 처리
  useEffect(() => {
    if (roomId && me) {
      chatsApi.markAsRead(roomId as string).catch(() => {})
    }
  }, [roomId, me])

  // 2500ms 폴링 (SM-C1 준수)
  const { data: polledMessages = [] } = useQuery<MessageResponse[]>({
    queryKey: ['chats', roomId, 'messages', lastIdRef.current],
    queryFn: () => chatsApi.getMessages(roomId as string, lastIdRef.current),
    refetchInterval: 2500,
    enabled: !!roomId,
  })

  // 서버 메시지 축적 + 낙관적 메시지 정리
  useEffect(() => {
    if (polledMessages.length > 0) {
      setAllMessages(prev => {
        const existingIds = new Set(prev.map(m => m.id))
        const newMsgs = polledMessages.filter(m => !existingIds.has(m.id))
        if (newMsgs.length === 0) return prev
        const updated = [...prev, ...newMsgs].sort((a, b) => a.id - b.id)
        lastIdRef.current = updated[updated.length - 1].id
        return updated
      })
      // 확인된 낙관적 메시지 제거
      setOptimisticMessages(prev =>
        prev.filter(om => !polledMessages.some(
          sm => sm.message === om.message && sm.sender_email === om.sender_email
        ))
      )
    }
  }, [polledMessages])

  // 새 메시지 도착 시 스크롤
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [allMessages, optimisticMessages])

  const handleSend = async () => {
    if (!input.trim() || sending || !postId || !myEmail) return
    const text = input.trim()
    const tempId = Date.now()
    setInput('')
    setSending(true)
    setOptimisticMessages(prev => [...prev, {
      tempId,
      message: text,
      sender_email: myEmail,
      sent_at: new Date().toISOString(),
      pending: true,
      error: false,
    }])
    try {
      await chatsApi.sendMessage(roomId as string, text, postId)
    } catch {
      setOptimisticMessages(prev =>
        prev.map(m => m.tempId === tempId ? { ...m, pending: false, error: true } : m)
      )
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const opponentEmail = myEmail === sellerEmail
    ? searchParams.get('buyerEmail') ?? '상대방'
    : sellerEmail

  return (
    <div className="min-h-screen bg-white flex flex-col max-w-lg mx-auto">
      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()} className="text-gray-600 text-lg">←</button>
        <div>
          <p className="font-semibold text-sm">{opponentEmail || '채팅'}</p>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto py-3">
        {allMessages.map(msg => (
          <ChatBubble
            key={msg.id}
            message={msg.message}
            isMine={msg.sender_email === myEmail}
          />
        ))}
        {optimisticMessages.map(om => (
          <ChatBubble
            key={om.tempId}
            message={om.message}
            isMine
            pending={om.pending}
            error={om.error}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="sticky bottom-0 border-t px-3 py-3 bg-white flex gap-2 items-end">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="메시지 입력..."
          className="flex-1 border rounded-full px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
          disabled={sending}
        />
        <button
          onClick={handleSend}
          disabled={sending || !input.trim()}
          className="w-10 h-10 rounded-full flex items-center justify-center text-white shrink-0 disabled:opacity-40"
          style={{ backgroundColor: '#FF7E36' }}
        >
          ➤
        </button>
      </div>
    </div>
  )
}
