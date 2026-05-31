'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'

const MENUS = [
  { label: '회원 관리', href: '/users' },
  { label: '거래 관리', href: '/posts' },
  { label: '채팅 관리', href: '/chats' },
]

export function AdminSidebar() {
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    router.push('/auth/login')
  }

  return (
    <aside className="w-56 min-h-screen bg-white border-r border-gray-100 flex flex-col">
      <div className="px-5 py-5 border-b border-gray-100">
        <span className="text-lg font-bold" style={{ color: '#FF7E36' }}>🥕 carrot 관리자</span>
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1">
        {MENUS.map((menu) => {
          const active = pathname.startsWith(menu.href)
          return (
            <Link
              key={menu.href}
              href={menu.href}
              className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? 'bg-orange-50 text-orange-700'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {menu.label}
            </Link>
          )
        })}
      </nav>

      <div className="px-3 py-4 border-t border-gray-100">
        <button
          onClick={handleLogout}
          className="w-full px-3 py-2 text-sm text-red-500 rounded-lg hover:bg-red-50 transition-colors text-left"
        >
          로그아웃
        </button>
      </div>
    </aside>
  )
}
