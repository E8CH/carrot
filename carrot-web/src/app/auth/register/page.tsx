'use client'

import { useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi } from '@/lib/api/auth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

interface FormState {
  email: string
  password: string
  address: string
  phone: string
}

export default function RegisterPage() {
  const router = useRouter()
  const [form, setForm] = useState<FormState>({
    email: '',
    password: '',
    address: '',
    phone: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (form.password.length < 8) {
      setError('비밀번호는 8자 이상이어야 합니다.')
      return
    }

    setLoading(true)

    // 401 인터셉터 pending promise 대응 — 30초 안전망
    timeoutRef.current = setTimeout(() => setLoading(false), 30_000)

    try {
      const data = await authApi.register(form)
      localStorage.setItem('token', data.access_token)
      router.push('/')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: unknown } } }
      const detail = axiosErr.response?.data?.detail
      // FastAPI 422 Pydantic 에러는 detail이 배열 [{loc, msg, type}]
      // AppException 에러는 detail이 문자열
      if (typeof detail === 'string') {
        setError(detail)
      } else if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0] as { msg?: string }
        setError(first.msg ?? '입력값을 확인해 주세요.')
      } else {
        setError('회원가입에 실패했습니다.')
      }
    } finally {
      clearTimeout(timeoutRef.current)
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold" style={{ color: '#FF7E36' }}>
            🥕 carrot
          </CardTitle>
          <CardDescription>새 계정을 만들어 중고거래를 시작하세요</CardDescription>
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
                value={form.email}
                onChange={handleChange}
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
                placeholder="8자 이상 입력하세요"
                value={form.password}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="address">주소</Label>
              <Input
                id="address"
                name="address"
                type="text"
                placeholder="서울시 강남구"
                value={form.address}
                onChange={handleChange}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="phone">연락처</Label>
              <Input
                id="phone"
                name="phone"
                type="tel"
                placeholder="010-0000-0000"
                value={form.phone}
                onChange={handleChange}
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
              {loading ? '가입 중...' : '가입하기'}
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center text-sm text-gray-500">
          이미 계정이 있으신가요?{' '}
          <Link href="/auth/login" className="ml-1 font-medium" style={{ color: '#FF7E36' }}>
            로그인
          </Link>
        </CardFooter>
      </Card>
    </div>
  )
}
