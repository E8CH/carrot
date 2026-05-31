'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { postsApi } from '@/lib/api/posts'
import { Button } from '@/components/ui/button'

interface Props {
  postId: number
  isOpen: boolean
  onClose: () => void
  onComplete: () => void
}

type Phase = 'select' | 'animating' | 'done'

export function TradeCompleteSheet({ postId, isOpen, onClose, onComplete }: Props) {
  const router = useRouter()
  const [buyers, setBuyers] = useState<string[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>('select')
  const [loading, setLoading] = useState(false)
  const [loadingBuyers, setLoadingBuyers] = useState(false)
  const [error, setError] = useState('')
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!isOpen) {
      setPhase('select')
      setSelected(null)
      setError('')
      setBuyers([])
      return
    }
    setLoadingBuyers(true)
    postsApi
      .getPostBuyers(postId)
      .then((r) => setBuyers(r.buyers.map((b) => b.buyer_email)))
      .catch(() => setError('구매자 목록을 불러오지 못했습니다.'))
      .finally(() => setLoadingBuyers(false))
  }, [isOpen, postId])

  useEffect(() => {
    return () => {
      if (timerRef.current !== null) clearTimeout(timerRef.current)
    }
  }, [])

  const handleConfirm = async () => {
    if (!selected || loading || phase !== 'select') return
    setLoading(true)
    setError('')
    try {
      await postsApi.completePost(postId, selected)
      setPhase('animating')
      timerRef.current = setTimeout(() => setPhase('done'), 1000)
    } catch {
      setError('거래완료 처리에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleWriteReview = () => {
    onComplete()
    onClose()
    if (selected) {
      router.push(`/reviews/${postId}?targetEmail=${encodeURIComponent(selected)}`)
    }
  }

  const handleSkipReview = () => {
    onComplete()
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40">
      <div className="bg-white w-full max-w-lg rounded-t-2xl p-6 space-y-4">
        {phase === 'select' && (
          <>
            <h2 className="text-base font-semibold">거래한 상대를 선택해 주세요</h2>
            {error && <p className="text-sm text-red-500">{error}</p>}
            {loadingBuyers && <p className="text-sm text-gray-400">구매자 목록 불러오는 중...</p>}
            {!loadingBuyers && buyers.length === 0 && !error && (
              <p className="text-sm text-gray-400">채팅한 구매자가 없습니다.</p>
            )}
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {buyers.map((email) => (
                <button
                  key={email}
                  onClick={() => setSelected(email)}
                  className={`w-full text-left px-4 py-3 rounded-lg border text-sm transition-colors ${
                    selected === email
                      ? 'border-orange-500 bg-orange-50 text-orange-700'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  {email}
                </button>
              ))}
            </div>
            <div className="flex gap-2 pt-2">
              <Button variant="outline" className="flex-1" onClick={onClose}>
                취소
              </Button>
              <Button
                className="flex-1"
                style={{ backgroundColor: selected && !loading ? '#FF7E36' : undefined }}
                disabled={!selected || loading || phase !== 'select'}
                onClick={handleConfirm}
              >
                {loading ? '처리 중...' : '거래완료 확정'}
              </Button>
            </div>
          </>
        )}

        {phase === 'animating' && (
          <div className="flex flex-col items-center py-8 gap-3">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-4xl animate-bounce">
              ✅
            </div>
            <p className="text-base font-semibold text-gray-800">거래가 완료됐어요!</p>
          </div>
        )}

        {phase === 'done' && (
          <div className="flex flex-col items-center py-4 gap-4">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center text-4xl">
              ✅
            </div>
            <p className="text-base font-semibold">거래가 완료됐어요!</p>
            <p className="text-sm text-gray-500 text-center">
              상대방에게 후기를 남겨 매너온도를 올려보세요.
            </p>
            <Button
              className="w-full"
              style={{ backgroundColor: '#FF7E36' }}
              onClick={handleWriteReview}
            >
              후기 작성하기
            </Button>
            <button className="text-sm text-gray-400 underline" onClick={handleSkipReview}>
              나중에 하기
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
