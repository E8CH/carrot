'use client'

import { useEffect, useState } from 'react'

export default function DashboardPage() {
  const [email, setEmail] = useState<string | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      try {
        const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
        const payload = JSON.parse(atob(base64))
        setEmail(payload.sub as string)
      } catch {
        // JWT decode 실패 시 이메일 미표시
      }
    }
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">대시보드</h1>
        {email && (
          <p className="text-sm text-gray-500 mt-1">환영합니다, {email} 관리자님</p>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        {[
          { label: '회원 관리', href: '/users', desc: '전체 회원 조회 및 계정 관리' },
          { label: '거래 관리', href: '/posts', desc: '게시글 현황 및 강제 삭제' },
          { label: '채팅 관리', href: '/chats', desc: '채팅 내역 조회 및 열람' },
        ].map((item) => (
          <a
            key={item.href}
            href={item.href}
            className="block p-5 bg-white rounded-xl border border-gray-100 hover:border-orange-300 hover:shadow-sm transition-all"
          >
            <h2 className="font-semibold text-gray-800 mb-1">{item.label}</h2>
            <p className="text-sm text-gray-500">{item.desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
