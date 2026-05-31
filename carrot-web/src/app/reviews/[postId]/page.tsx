'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { reviewsApi } from '@/lib/api/reviews'
import { Button } from '@/components/ui/button'

const POSITIVE_TAGS = ['시간 약속을 잘 지켜요', '친절하고 매너 있어요', '물건 상태가 설명과 같아요', '거래 후 연락도 잘 돼요']
const NEGATIVE_TAGS = ['시간 약속을 안 지켜요', '불친절했어요', '물건 상태가 설명과 달라요', '연락이 잘 안 돼요']

export default function ReviewFormPage() {
  const { postId } = useParams<{ postId: string }>()
  const searchParams = useSearchParams()
  const router = useRouter()
  const targetEmail = searchParams.get('targetEmail') ?? ''

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const [isPositive, setIsPositive] = useState<boolean | null>(null)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    return () => {
      if (timeoutRef.current !== null) clearTimeout(timeoutRef.current)
    }
  }, [])

  const currentTags = isPositive === true ? POSITIVE_TAGS : isPositive === false ? NEGATIVE_TAGS : []

  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    )
  }

  const handleSentimentChange = (positive: boolean) => {
    setIsPositive(positive)
    setSelectedTags([])
  }

  const handleSubmit = async () => {
    if (isPositive === null) { setError('긍정 또는 부정을 선택해 주세요.'); return }
    setSubmitting(true)
    setError('')
    try {
      await reviewsApi.createReview({
        post_id: Number(postId),
        is_positive: isPositive,
        tags: selectedTags,
        comment: comment.trim() || null,
      })
      setSuccess(true)
      timeoutRef.current = setTimeout(() => router.back(), 1500)
    } catch {
      setError('후기 작성에 실패했습니다. 이미 작성했거나 권한이 없을 수 있습니다.')
    } finally {
      setSubmitting(false)
    }
  }

  if (success) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 text-center px-4">
        <div className="text-5xl">🥕</div>
        <p className="text-lg font-semibold text-gray-800">후기가 등록됐어요!</p>
        <p className="text-sm text-gray-500">매너온도가 업데이트됩니다.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white max-w-2xl mx-auto pb-24">
      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3 flex items-center gap-3">
        <button onClick={() => router.back()} className="text-gray-600 text-lg">←</button>
        <span className="font-semibold flex-1">후기 작성</span>
      </header>

      <div className="px-4 py-6 space-y-6">
        <div>
          <p className="text-sm text-gray-500 mb-1">거래 상대</p>
          <p className="text-base font-medium text-gray-800">{targetEmail || '알 수 없음'}</p>
        </div>

        {/* 긍정/부정 선택 */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-3">거래는 어떠셨나요?</p>
          <div className="flex gap-3">
            <button
              onClick={() => handleSentimentChange(true)}
              className={`flex-1 py-3 rounded-xl border-2 text-sm font-medium transition-colors ${
                isPositive === true
                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                  : 'border-gray-200 text-gray-500'
              }`}
            >
              ❤️ 좋았어요
            </button>
            <button
              onClick={() => handleSentimentChange(false)}
              className={`flex-1 py-3 rounded-xl border-2 text-sm font-medium transition-colors ${
                isPositive === false
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-500'
              }`}
            >
              💔 별로였어요
            </button>
          </div>
        </div>

        {/* 태그 선택 */}
        {currentTags.length > 0 && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">어떤 점이 {isPositive ? '좋았나요?' : '별로였나요?'}</p>
            <div className="flex flex-wrap gap-2">
              {currentTags.map((tag) => (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={`px-3 py-1.5 rounded-full border text-sm transition-colors ${
                    selectedTags.includes(tag)
                      ? 'border-orange-500 bg-orange-50 text-orange-700'
                      : 'border-gray-200 text-gray-600'
                  }`}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 코멘트 */}
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">한 줄 후기 (선택)</p>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value.slice(0, 500))}
            placeholder="상대방에 대한 후기를 남겨 주세요."
            rows={3}
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-800 resize-none focus:outline-none focus:border-orange-400"
          />
          <p className="text-xs text-gray-400 text-right mt-1">{comment.length}/500</p>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}
      </div>

      <div className="fixed bottom-0 left-0 right-0 max-w-2xl mx-auto bg-white border-t px-4 py-3">
        <Button
          className="w-full"
          style={{ backgroundColor: isPositive !== null ? '#FF7E36' : undefined }}
          disabled={isPositive === null || submitting}
          onClick={handleSubmit}
        >
          {submitting ? '제출 중...' : '후기 제출하기'}
        </Button>
      </div>
    </div>
  )
}
