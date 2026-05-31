'use client'

import { useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi } from '@/lib/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    timeoutRef.current = setTimeout(() => setLoading(false), 30_000)

    try {
      const data = await authApi.login({ email, password })
      localStorage.setItem('token', data.access_token)
      router.push('/')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: unknown } } }
      const detail = axiosErr.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as { msg?: string }
        setError(first.msg ?? '입력값을 확인해 주세요.')
      } else {
        setError('로그인에 실패했습니다.')
      }
    } finally {
      clearTimeout(timeoutRef.current)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="fixed top-4 left-4">
        <Link href="/" className="text-sm text-gray-500 hover:text-gray-700">← 홈</Link>
      </div>
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold" style={{ color: '#FF7E36' }}>
            🥕 carrot
          </CardTitle>
          <CardDescription>이메일과 비밀번호로 로그인하세요</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="email">이메일</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="example@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="password">비밀번호</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="비밀번호 입력"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {error && (
              <p className="text-red-500 text-sm" role="alert">
                {error}
              </p>
            )}

            <Button
              type="submit"
              className="w-full"
              style={{ backgroundColor: '#FF7E36' }}
              disabled={loading}
            >
              {loading ? '로그인 중...' : '로그인'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-sm text-gray-500">
          아직 계정이 없으신가요?{' '}
          <Link href="/auth/register" className="ml-1 font-medium" style={{ color: '#FF7E36' }}>
            회원가입
          </Link>
        </CardFooter>
      </Card>
    </div>
  )
}
