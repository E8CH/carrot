'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { chatsApi } from '@/lib/api/chats'
import { postsApi } from '@/lib/api/posts'
import { usersApi } from '@/lib/api/users'
import { StatusBadge } from '@/components/common/StatusBadge'
import { MannerTempWidget } from '@/components/common/MannerTempWidget'
import { TradeCompleteSheet } from '@/components/posts/TradeCompleteSheet'
import { Button } from '@/components/ui/button'

// ─── ImageSlider ─────────────────────────────────────────────────────────────

function ImageSlider({ photos }: { photos: string[] }) {
  const [idx, setIdx] = useState(0)
  const startX = useRef(0)
  const isDragging = useRef(false)

  const prev = () => setIdx((i) => Math.max(0, i - 1))
  const next = () => setIdx((i) => Math.min(photos.length - 1, i + 1))

  if (photos.length === 0) {
    return (
      <div className="w-full h-60 bg-gray-100 flex items-center justify-center text-gray-300 text-5xl">
        🖼️
      </div>
    )
  }

  return (
    <div
      className="relative w-full h-60 overflow-hidden bg-gray-100 select-none"
      onPointerDown={(e) => {
        startX.current = e.clientX
        isDragging.current = true
        e.currentTarget.setPointerCapture(e.pointerId)
      }}
      onPointerUp={(e) => {
        if (!isDragging.current) return
        isDragging.current = false
        const diff = e.clientX - startX.current
        if (diff > 50) prev()
        else if (diff < -50) next()
      }}
      onPointerCancel={() => { isDragging.current = false }}
    >
      <div
        className="flex h-full transition-transform duration-300 ease-out"
        style={{ transform: `translateX(-${idx * 100 / photos.length}%)`, width: `${photos.length * 100}%` }}
      >
        {photos.map((url, i) => (
          <div
            key={i}
            className="relative flex-shrink-0 h-full"
            style={{ width: `${100 / photos.length}%` }}
          >
            <Image
              src={url}
              alt={`사진 ${i + 1}`}
              fill
              className="object-cover"
              priority={i === 0}
              sizes="(max-width: 512px) 100vw, 512px"
            />
          </div>
        ))}
      </div>
      {photos.length > 1 && (
        <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
          {photos.map((_, i) => (
            <div
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-colors ${
                i === idx ? 'bg-white' : 'bg-white/50'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function PostDetailPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const queryClient = useQueryClient()
  const postId = Number(id)

  const { data: post, isLoading, isError } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => postsApi.getPost(postId),
    enabled: !Number.isNaN(postId),
  })

  const { data: me } = useQuery({
    queryKey: ['me'],
    queryFn: () => usersApi.getMe().catch(() => null),
    retry: false,
  })

  const [showDeleteDialog, setShowDeleteDialog] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState('')
  const [isLiked, setIsLiked] = useState(false)
  const [likeCount, setLikeCount] = useState(0)

  useEffect(() => {
    if (post) {
      setIsLiked(post.is_liked)
      setLikeCount(post.like_count)
    }
  }, [post])

  const [chatLoading, setChatLoading] = useState(false)
  const [chatError, setChatError] = useState('')

  const handleChat = async () => {
    if (!me) { router.push('/auth/login'); return }
    setChatLoading(true)
    setChatError('')
    try {
      const room = await chatsApi.createOrGetRoom(postId)
      router.push(
        `/chat/${room.room_id}?postId=${room.post_id}&sellerEmail=${encodeURIComponent(room.seller_email)}&buyerEmail=${encodeURIComponent(room.buyer_email)}`
      )
    } catch {
      setChatError('채팅방 연결에 실패했습니다.')
    } finally {
      setChatLoading(false)
    }
  }

  const [statusLoading, setStatusLoading] = useState(false)
  const [statusError, setStatusError] = useState('')
  const [showTradeSheet, setShowTradeSheet] = useState(false)

  const handleStatusChange = async (newStatus: string) => {
    if (statusLoading) return
    setStatusLoading(true)
    setStatusError('')
    try {
      await postsApi.changeStatus(postId, newStatus)
      queryClient.invalidateQueries({ queryKey: ['post', postId] })
    } catch {
      setStatusError('상태 변경에 실패했습니다.')
    } finally {
      setStatusLoading(false)
    }
  }

  const handleLike = async () => {
    if (!me) { router.push('/auth/login'); return }
    const prev = { isLiked, likeCount }
    setIsLiked(!isLiked)
    setLikeCount(isLiked ? likeCount - 1 : likeCount + 1)
    try {
      const result = await postsApi.toggleLike(postId)
      setIsLiked(result.is_liked)
      setLikeCount(result.like_count)
    } catch {
      setIsLiked(prev.isLiked)
      setLikeCount(prev.likeCount)
    }
  }

  const handleDelete = async () => {
    setDeleting(true)
    setDeleteError('')
    try {
      await postsApi.deletePost(postId)
      router.push('/')
    } catch {
      setShowDeleteDialog(false)
      setDeleting(false)
      setDeleteError('삭제에 실패했습니다. 다시 시도해주세요.')
    }
  }

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">불러오는 중...</div>
  }

  if (isError || !post) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 text-gray-400">
        <p>게시글을 찾을 수 없습니다.</p>
        <button onClick={() => router.push('/')} className="text-sm underline">홈으로</button>
      </div>
    )
  }

  const isOwner = !!me && me.email === post.seller_email
  const priceText = post.is_free ? '나눔' : post.price != null ? `${post.price.toLocaleString()}원` : '가격 미정'

  return (
    <div className="min-h-screen bg-white max-w-lg mx-auto pb-24">
      {/* 삭제 확인 다이얼로그 */}
      {showDeleteDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl p-6 mx-4 shadow-xl max-w-sm w-full">
            <h2 className="font-semibold text-base mb-2">게시글을 삭제할까요?</h2>
            <p className="text-sm text-gray-500 mb-5">삭제하면 복구할 수 없습니다.</p>
            {deleteError && <p className="text-sm text-red-500 mb-3">{deleteError}</p>}
            <div className="flex gap-2">
              <button
                onClick={() => setShowDeleteDialog(false)}
                disabled={deleting}
                className="flex-1 py-2.5 rounded-lg border text-sm text-gray-600 disabled:opacity-40"
              >취소</button>
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 py-2.5 rounded-lg text-sm font-medium text-white bg-red-500 disabled:opacity-40"
              >{deleting ? '삭제 중...' : '삭제'}</button>
            </div>
          </div>
        </div>
      )}

      {/* 헤더 */}
      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()} className="text-gray-600 text-lg">←</button>
        <span className="font-semibold flex-1 truncate">{post.title}</span>
      </header>

      {/* 이미지 슬라이더 */}
      <ImageSlider photos={post.photos} />

      {/* 판매자 프로필 */}
      <div className="flex items-center gap-3 px-4 py-3 border-b">
        <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center text-lg">👤</div>
        <div>
          <p className="text-sm font-medium text-gray-900">{post.seller_email}</p>
          <MannerTempWidget temp={post.manner_temp} />
        </div>
      </div>

      {/* 본문 */}
      <div className="px-4 py-4 space-y-3">
        {/* 제목 + 상태 배지 */}
        <div className="flex items-center gap-2">
          <h1 className="text-lg font-semibold text-gray-900 flex-1">{post.title}</h1>
          <StatusBadge status={post.status} />
        </div>

        {/* 가격 */}
        <p className="text-xl font-bold text-gray-900">{priceText}</p>

        {/* 설명 */}
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{post.description}</p>

        {/* 거래 희망 장소 */}
        {post.trade_place && (
          <p className="text-sm text-gray-400">📍 {post.trade_place}</p>
        )}

        {/* 통계 */}
        <div className="flex gap-3 text-xs text-gray-400 pt-2 border-t">
          <span>채팅 {post.chat_count}</span>
          <span>관심 {post.like_count}</span>
          <span>조회 {post.view_count}</span>
        </div>
      </div>

      {/* 하단 고정 버튼 */}
      <div className="fixed bottom-0 left-0 right-0 max-w-lg mx-auto bg-white border-t px-4 py-3 flex flex-col gap-2">
        {chatError && <p className="text-xs text-red-500 text-center">{chatError}</p>}
        {statusError && <p className="text-xs text-red-500 text-center">{statusError}</p>}
        <div className="flex gap-2">
        {isOwner ? (
          <>
            {post.status !== '거래완료' && (
              <>
                <Button
                  variant="outline"
                  className="shrink-0 text-sm px-3 text-orange-600 border-orange-400 hover:bg-orange-50"
                  onClick={() => setShowTradeSheet(true)}
                >
                  거래완료
                </Button>
                <Button
                  variant="outline"
                  className="shrink-0 text-sm px-3"
                  onClick={() => handleStatusChange(post.status === '판매중' ? '예약중' : '판매중')}
                  disabled={statusLoading}
                >
                  {post.status === '판매중' ? '예약중' : '판매중'}
                </Button>
              </>
            )}
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => router.push(`/posts/${post.id}/edit`)}
            >
              수정
            </Button>
            <Button
              variant="outline"
              className="flex-1 text-red-500 border-red-300 hover:bg-red-50"
              onClick={() => setShowDeleteDialog(true)}
            >
              삭제
            </Button>
          </>
        ) : (
          <>
            <Button
              variant="outline"
              className="w-14 h-12 shrink-0 text-lg"
              onClick={handleLike}
              aria-label={isLiked ? '찜 해제' : '찜하기'}
            >
              {isLiked ? '❤️' : '🤍'}
              <span className="text-xs ml-0.5">{likeCount}</span>
            </Button>
            <Button
              className="flex-1"
              style={{ backgroundColor: chatLoading ? '#FFB899' : '#FF7E36' }}
              onClick={handleChat}
              disabled={chatLoading}
            >
              {chatLoading ? '연결 중...' : '채팅하기'}
            </Button>
          </>
        )}
        </div>
      </div>
      <TradeCompleteSheet
        postId={postId}
        isOpen={showTradeSheet}
        onClose={() => setShowTradeSheet(false)}
        onComplete={() => {
          setShowTradeSheet(false)
          queryClient.invalidateQueries({ queryKey: ['post', postId] })
        }}
      />
    </div>
  )
}
