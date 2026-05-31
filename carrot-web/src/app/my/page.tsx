'use client'

import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { usersApi } from '@/lib/api/users'
import { postsApi } from '@/lib/api/posts'
import { MannerTempWidget } from '@/components/common/MannerTempWidget'
import { PostCard } from '@/components/common/PostCard'
import { SiteHeader } from '@/components/layout/SiteHeader'

function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const STATUS_FILTERS = [
  { label: '전체', value: null },
  { label: '판매중', value: '판매중' },
  { label: '예약중', value: '예약중' },
  { label: '거래완료', value: '거래완료' },
]

export default function MyPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null)
  const [changingId, setChangingId] = useState<number | null>(null)

  const { data: profile, isLoading, isError } = useQuery({
    queryKey: ['users', 'me'],
    queryFn: usersApi.getMe,
  })

  const { data: myPostsData, isLoading: postsLoading } = useQuery({
    queryKey: ['users', 'me', 'posts', selectedStatus],
    queryFn: () => usersApi.getMyPosts(selectedStatus ?? undefined),
  })

  const { data: purchasesData, isLoading: purchasesLoading } = useQuery({
    queryKey: ['users', 'me', 'purchases'],
    queryFn: usersApi.getMyPurchases,
  })

  const { data: likesData, isLoading: likesLoading } = useQuery({
    queryKey: ['users', 'me', 'likes'],
    queryFn: usersApi.getMyLikes,
  })

  const handleLogout = () => {
    localStorage.removeItem('token')
    router.push('/auth/login')
  }

  const handleStatusChange = async (id: number, newStatus: string) => {
    setChangingId(id)
    try {
      await postsApi.changeStatus(id, newStatus)
      queryClient.invalidateQueries({ queryKey: ['users', 'me', 'posts'] })
    } finally {
      setChangingId(null)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-gray-400">불러오는 중...</div>
      </div>
    )
  }

  if (isError || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-500">프로필을 불러올 수 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 max-w-lg mx-auto">
      <SiteHeader />
      <div className="px-4 py-8">

      {/* 프로필 카드 */}
      <div className="bg-white rounded-xl p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-gray-500 text-sm">매너온도</span>
          <MannerTempWidget temp={profile.manner_temp} />
        </div>

        <hr className="border-gray-100" />

        <div className="space-y-3">
          <div>
            <p className="text-xs text-gray-400">이메일</p>
            <p className="text-gray-800">{profile.email}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">주소</p>
            <p className="text-gray-800">{profile.address}</p>
          </div>
          <div>
            <p className="text-xs text-gray-400">연락처</p>
            <p className="text-gray-800">{profile.phone}</p>
          </div>
        </div>
      </div>

      {/* 판매관리 섹션 */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">판매관리</h2>

        {/* 상태 필터 탭 */}
        <div className="flex gap-2 overflow-x-auto pb-1 mb-4">
          {STATUS_FILTERS.map(({ label, value }) => {
            const active = selectedStatus === value
            return (
              <button
                key={label}
                onClick={() => setSelectedStatus(value)}
                className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                  active
                    ? 'border-orange-500 bg-orange-50 text-orange-700'
                    : 'border-gray-200 text-gray-500 hover:bg-gray-50'
                }`}
              >
                {label}
              </button>
            )
          })}
        </div>

        {/* 게시글 목록 */}
        {postsLoading ? (
          <div className="py-10 text-center text-gray-400 text-sm">불러오는 중...</div>
        ) : !myPostsData || myPostsData.items.length === 0 ? (
          <div className="py-10 text-center text-gray-400 text-sm">등록한 게시글이 없어요.</div>
        ) : (
          <div className="bg-white rounded-xl overflow-hidden shadow-sm">
            {myPostsData.items.map((post) => (
              <div key={post.id} className="border-b border-gray-100 last:border-0">
                <PostCard
                  id={post.id}
                  title={post.title}
                  price={post.price}
                  is_free={post.is_free}
                  status={post.status}
                  thumbnail={post.thumbnail}
                  chat_count={post.chat_count}
                  like_count={post.like_count}
                  created_at={post.created_at}
                />
                {/* 상태 변경 버튼 */}
                {post.status !== '거래완료' && (
                  <div className="px-4 pb-3 flex gap-2">
                    {post.status === '판매중' && (
                      <button
                        disabled={changingId === post.id}
                        onClick={() => handleStatusChange(post.id, '예약중')}
                        className="text-xs px-3 py-1 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
                      >
                        {changingId === post.id ? '변경 중...' : '예약중으로 변경'}
                      </button>
                    )}
                    {post.status === '예약중' && (
                      <button
                        disabled={changingId === post.id}
                        onClick={() => handleStatusChange(post.id, '판매중')}
                        className="text-xs px-3 py-1 rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50 disabled:opacity-50 transition-colors"
                      >
                        {changingId === post.id ? '변경 중...' : '판매중으로 변경'}
                      </button>
                    )}
                    <Link
                      href={`/posts/${post.id}`}
                      className="text-xs px-3 py-1 rounded-full border border-orange-300 text-orange-600 hover:bg-orange-50 transition-colors"
                    >
                      상세 보기
                    </Link>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 구매내역 섹션 */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">구매내역</h2>
        {purchasesLoading ? (
          <div className="py-10 text-center text-gray-400 text-sm">불러오는 중...</div>
        ) : !purchasesData || purchasesData.items.length === 0 ? (
          <div className="py-10 text-center text-gray-400 text-sm">구매내역이 없어요.</div>
        ) : (
          <div className="bg-white rounded-xl overflow-hidden shadow-sm">
            {purchasesData.items.map((item) => (
              <Link
                key={item.id}
                href={`/posts/${item.id}`}
                className="flex items-center gap-3 p-3 border-b border-gray-100 last:border-0 hover:bg-gray-50 transition-colors"
              >
                <div className="relative w-[60px] h-[60px] rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                  {item.thumbnail ? (
                    <Image src={item.thumbnail} alt={item.title} fill className="object-cover" sizes="60px" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-300 text-2xl">🖼️</div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 line-clamp-1">{item.title}</p>
                  <p className="text-sm text-gray-700 mt-0.5">
                    {item.is_free ? '나눔' : item.price != null ? `${item.price.toLocaleString()}원` : '가격 미정'}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">거래완료 {formatDate(item.updated_at)}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* 관심목록 섹션 */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">관심목록</h2>
        {likesLoading ? (
          <div className="py-10 text-center text-gray-400 text-sm">불러오는 중...</div>
        ) : !likesData || likesData.items.length === 0 ? (
          <div className="py-10 text-center text-gray-400 text-sm">관심목록이 없어요.</div>
        ) : (
          <div className="bg-white rounded-xl overflow-hidden shadow-sm">
            {likesData.items.map((post) => (
              <PostCard key={post.id} {...post} />
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 space-y-2">
        <button
          onClick={handleLogout}
          className="w-full py-3 text-sm text-red-500 border border-red-200 rounded-xl hover:bg-red-50 transition-colors"
        >
          로그아웃
        </button>
      </div>
      </div>
    </div>
  )
}
