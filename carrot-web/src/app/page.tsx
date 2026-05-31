'use client'

import { useEffect, useRef, useState } from 'react'
import { useInfiniteQuery, useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { PostCard } from '@/components/common/PostCard'
import { postsApi } from '@/lib/api/posts'
import { chatsApi } from '@/lib/api/chats'

export default function Home() {
  const bottomRef = useRef<HTMLDivElement>(null)
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem('token'))
  }, [])

  const { data: unreadData } = useQuery({
    queryKey: ['unread-count'],
    queryFn: () => chatsApi.getUnreadCount().catch(() => ({ count: 0 })),
    refetchInterval: 5000,
    enabled: isLoggedIn,
  })

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
  } = useInfiniteQuery({
    queryKey: ['posts'],
    queryFn: ({ pageParam }) => postsApi.getPosts(pageParam as number),
    initialPageParam: 1,
    getNextPageParam: (lastPage, _allPages, lastPageParam) =>
      // API 응답의 size 필드와 비교하여 다음 페이지 여부 결정
      lastPage.items.length >= lastPage.size ? (lastPageParam as number) + 1 : undefined,
  })

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage()
      }
    })
    const el = bottomRef.current
    if (el) observer.observe(el)
    return () => observer.disconnect()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const allPosts = data?.pages.flatMap((page) => page.items) ?? []

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <span className="text-xl font-bold" style={{ color: '#FF7E36' }}>🥕 carrot</span>
        <div className="flex items-center gap-3">
          <Link href="/posts/new" className="text-sm font-medium" style={{ color: '#FF7E36' }}>글쓰기</Link>
          <Link href="/chat" className="relative text-sm text-gray-500 hover:text-gray-700">
            채팅
            {isLoggedIn && (unreadData?.count ?? 0) > 0 && (
              <span className="absolute -top-2 -right-3 min-w-[16px] h-4 px-1 rounded-full text-white text-[10px] flex items-center justify-center" style={{ backgroundColor: '#FF7E36' }}>
                {(unreadData?.count ?? 0) > 99 ? '99+' : unreadData?.count}
              </span>
            )}
          </Link>
          <Link href="/my" className="text-sm text-gray-500 hover:text-gray-700">나의당근</Link>
          {!isLoggedIn && (
            <Link href="/auth/login" className="text-sm text-gray-500 hover:text-gray-700">로그인</Link>
          )}
        </div>
      </header>

      <main className="max-w-lg mx-auto">
        {isLoading && (
          <div className="p-8 text-center text-gray-400">불러오는 중...</div>
        )}
        {isError && (
          <div className="p-8 text-center text-red-400">게시글을 불러올 수 없습니다.</div>
        )}

        {allPosts.map((post) => (
          <PostCard key={post.id} {...post} />
        ))}

        <div ref={bottomRef} className="h-4" />

        {isFetchingNextPage && (
          <div className="p-4 text-center text-gray-400 text-sm">더 불러오는 중...</div>
        )}
        {!hasNextPage && allPosts.length > 0 && (
          <div className="p-4 text-center text-gray-300 text-sm">마지막 게시글입니다.</div>
        )}
      </main>
    </div>
  )
}
