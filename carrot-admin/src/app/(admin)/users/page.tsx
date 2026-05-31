'use client'

import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { adminUsersApi } from '@/lib/api/admin-users'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

export default function UsersPage() {
  const queryClient = useQueryClient()
  const [toast, setToast] = useState<string | null>(null)
  const [updatingEmail, setUpdatingEmail] = useState<string | null>(null)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: adminUsersApi.getUsers,
  })

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const handleToggleStatus = async (email: string, currentActive: boolean) => {
    setUpdatingEmail(email)
    try {
      await adminUsersApi.updateStatus(email, !currentActive)
      queryClient.invalidateQueries({ queryKey: ['admin', 'users'] })
      showToast(currentActive ? `${email} 비활성화 완료` : `${email} 활성화 완료`)
    } catch {
      showToast('상태 변경에 실패했습니다.')
    } finally {
      setUpdatingEmail(null)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">회원 관리</h1>
        {data && <span className="text-sm text-gray-500">전체 {data.total}명</span>}
      </div>

      {toast && (
        <div className="fixed top-4 right-4 z-50 bg-gray-800 text-white px-4 py-2 rounded-lg text-sm shadow-lg">
          {toast}
        </div>
      )}

      {isLoading && <div className="py-20 text-center text-gray-400">불러오는 중...</div>}
      {isError && <div className="py-20 text-center text-red-500">회원 목록을 불러올 수 없습니다.</div>}

      {data && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">이메일</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">가입일</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">매너온도</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">게시글</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">상태</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">작업</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {data.items.map((user) => (
                <tr key={user.email} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 text-gray-800 font-medium">{user.email}</td>
                  <td className="px-4 py-3 text-gray-500">{formatDate(user.created_at)}</td>
                  <td className="px-4 py-3 text-center text-gray-700">{user.manner_temp.toFixed(1)}℃</td>
                  <td className="px-4 py-3 text-center text-gray-600">{user.post_count}</td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
                        user.is_active
                          ? 'bg-green-50 text-green-700'
                          : 'bg-red-50 text-red-600'
                      }`}
                    >
                      {user.is_active ? '활성' : '비활성'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      disabled={updatingEmail === user.email}
                      onClick={() => handleToggleStatus(user.email, user.is_active)}
                      className={`px-3 py-1 text-xs rounded-lg border transition-colors disabled:opacity-50 ${
                        user.is_active
                          ? 'border-red-200 text-red-600 hover:bg-red-50'
                          : 'border-green-200 text-green-700 hover:bg-green-50'
                      }`}
                    >
                      {updatingEmail === user.email
                        ? '처리 중...'
                        : user.is_active
                        ? '비활성화'
                        : '활성화'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
