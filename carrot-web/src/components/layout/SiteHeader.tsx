'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { chatsApi } from '@/lib/api/chats'

export function SiteHeader() {
  const router = useRouter()
  const pathname = usePathname()
  const queryClient = useQueryClient()
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem('token'))
  }, [])

  const { data: unreadData } = useQuery({
    queryKey: ['unread-count'],
    queryFn: () => chatsApi.getUnreadCount().catch(() => ({ count: 0 })),
    refetchInterval: 3000,
    staleTime: 0,
    enabled: isLoggedIn,
  })

  const handleLogoClick = () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] })
    router.push('/')
    router.refresh()
  }

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between">
      <button onClick={handleLogoClick} className="text-xl font-bold" style={{ color: '#FF7E36' }}>
        🥕 carrot
      </button>
      <div className="flex items-center gap-3">
        <Link
          href="/posts/new"
          className={`text-sm font-medium ${pathname === '/posts/new' ? 'text-orange-500' : 'text-gray-500 hover:text-gray-700'}`}
        >
          글쓰기
        </Link>
        <Link
          href="/chat"
          className={`relative text-sm font-medium ${pathname.startsWith('/chat') ? 'text-orange-500' : 'text-gray-500 hover:text-gray-700'}`}
        >
          채팅
          {isLoggedIn && (unreadData?.count ?? 0) > 0 && (
            <span className="absolute -top-2 -right-3 min-w-[16px] h-4 px-1 rounded-full text-white text-[10px] flex items-center justify-center" style={{ backgroundColor: '#FF7E36' }}>
              {(unreadData?.count ?? 0) > 99 ? '99+' : unreadData?.count}
            </span>
          )}
        </Link>
        <Link
          href="/my"
          className={`text-sm font-medium ${pathname === '/my' ? 'text-orange-500' : 'text-gray-500 hover:text-gray-700'}`}
        >
          나의당근
        </Link>
        {!isLoggedIn && (
          <Link
            href="/auth/login"
            className={`text-sm font-medium ${pathname.startsWith('/auth') ? 'text-orange-500' : 'text-gray-500 hover:text-gray-700'}`}
          >
            로그인
          </Link>
        )}
      </div>
    </header>
  )
}
