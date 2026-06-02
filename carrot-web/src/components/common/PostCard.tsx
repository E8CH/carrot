'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { StatusBadge } from './StatusBadge'

function timeAgo(date: string): string {
  const diff = Date.now() - new Date(date).getTime()
  const mins = Math.floor(diff / 60_000)
  if (mins < 1) return '방금 전'
  if (mins < 60) return `${mins}분 전`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}시간 전`
  return `${Math.floor(hours / 24)}일 전`
}

interface PostCardProps {
  id: number
  title: string
  price: number | null
  is_free: boolean
  status: string
  thumbnail: string | null
  chat_count: number
  like_count: number
  created_at: string
}

function ThumbnailImage({ src, alt }: { src: string; alt: string }) {
  const [loaded, setLoaded] = useState(false)
  return (
    <>
      <Image
        src={src}
        alt={alt}
        fill
        className={`object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        sizes="100px"
        onLoad={() => setLoaded(true)}
      />
      {!loaded && <div className="absolute inset-0 bg-gray-200 animate-pulse" />}
    </>
  )
}

export function PostCard({
  id,
  title,
  price,
  is_free,
  status,
  thumbnail,
  chat_count,
  like_count,
  created_at,
}: PostCardProps) {
  const priceText = is_free ? '나눔' : price != null ? `${price.toLocaleString()}원` : '가격 미정'

  return (
    <Link href={`/posts/${id}`} className="flex gap-3 p-4 bg-white hover:bg-gray-50 transition-colors border-b border-gray-100">
      {/* 썸네일 100×100 */}
      <div className="relative flex-shrink-0 w-[100px] h-[100px] rounded-xl overflow-hidden bg-gray-100">
        {thumbnail ? (
          <ThumbnailImage src={thumbnail} alt={title} />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-3xl">🖼️</div>
        )}
        {/* 상태 배지 좌상단 오버레이 */}
        <div className="absolute top-1 left-1">
          <StatusBadge status={status} />
        </div>
      </div>

      {/* 텍스트 영역 */}
      <div className="flex-1 min-w-0 flex flex-col justify-between py-1">
        <p className="text-base font-medium text-gray-900 line-clamp-2">{title}</p>
        <p className="text-sm font-semibold text-gray-900 mt-1">{priceText}</p>
        <div className="flex items-center gap-2 mt-1 text-xs text-gray-400">
          <span>채팅 {chat_count}</span>
          <span>관심 {like_count}</span>
          <span>{timeAgo(created_at)}</span>
        </div>
      </div>
    </Link>
  )
}
