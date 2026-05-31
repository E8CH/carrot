'use client'

import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { adminPostsApi } from '@/lib/api/admin-posts'

const STATUS_FILTERS = [
  { label: '전체', value: undefined as string | undefined },
  { label: '판매중', value: '판매중' },
  { label: '예약중', value: '예약중' },
  { label: '거래완료', value: '거래완료' },
]

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function PostsPage() {
  const queryClient = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined)
  const [toast, setToast] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'posts', statusFilter],
    queryFn: () => adminPostsApi.getPosts(statusFilter),
  })

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const handleDelete = async (id: number, title: string) => {
    if (!window.confirm(`"${title}" 게시글을 강제 삭제하시겠습니까?`)) return
    setDeletingId(id)
    try {
      await adminPostsApi.deletePost(id)
      queryClient.invalidateQueries({ queryKey: ['admin', 'posts'] })
      showToast('게시글이 삭제되었습니다.')
    } catch {
      showToast('삭제에 실패했습니다.')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">거래 관리</h1>
        {data && <span className="text-sm text-gray-500">전체 {data.total}건</span>}
      </div>

      {toast && (
        <div className="fixed top-4 right-4 z-50 bg-gray-800 text-white px-4 py-2 rounded-lg text-sm shadow-lg">
          {toast}
        </div>
      )}

      <div className="flex gap-2">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.label}
            onClick={() => setStatusFilter(f.value)}
            className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
              statusFilter === f.value
                ? 'bg-orange-500 text-white border-orange-500'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && (
        <div className="py-20 text-center text-gray-400">불러오는 중...</div>
      )}
      {isError && (
        <div className="py-20 text-center text-red-500">
          게시글 목록을 불러올 수 없습니다.
        </div>
      )}

      {data && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">제목</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">판매자</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">가격</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">상태</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">등록일</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {data.items.map((post) => (
                <tr key={post.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-800 font-medium max-w-[200px] truncate">
                    {post.title}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{post.seller_email}</td>
                  <td className="px-4 py-3 text-center text-gray-700">
                    {post.is_free
                      ? '나눔'
                      : post.price
                      ? `${post.price.toLocaleString()}원`
                      : '-'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        post.status === '판매중'
                          ? 'bg-green-50 text-green-700'
                          : post.status === '예약중'
                          ? 'bg-yellow-50 text-yellow-700'
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {post.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {formatDate(post.created_at)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      disabled={deletingId === post.id}
                      onClick={() => handleDelete(post.id, post.title)}
                      className="px-3 py-1 text-xs rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition-colors disabled:opacity-50"
                    >
                      {deletingId === post.id ? '삭제 중...' : '강제삭제'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {data.items.length === 0 && (
            <div className="py-16 text-center text-gray-400">게시글이 없습니다.</div>
          )}
        </div>
      )}
    </div>
  )
}
