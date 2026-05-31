'use client'

import { useEffect, useRef } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { PostCard } from '@/components/common/PostCard'
import { postsApi } from '@/lib/api/posts'
import { SiteHeader } from '@/components/layout/SiteHeader'

export default function Home() {
  const bottomRef = useRef<HTMLDivElement>(null)

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
      <SiteHeader />

      <main className="px-4 lg:px-10">
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <div className="w-8 h-8 border-4 border-orange-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-400">불러오는 중...</p>
          </div>
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
