'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { postsApi, type DraftResponse } from '@/lib/api/posts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const MAX_FILE_SIZE = 5 * 1024 * 1024  // 5MB
const MAX_PHOTOS = 10

export default function NewPostPage() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const previewsRef = useRef<string[]>([])

  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [isFree, setIsFree] = useState(false)
  const [tradePlace, setTradePlace] = useState('')
  const [error, setError] = useState('')
  const [fileError, setFileError] = useState('')
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState('')
  const [draftDialog, setDraftDialog] = useState<DraftResponse | null>(null)
  const [showBackDialog, setShowBackDialog] = useState(false)
  const [draftSaving, setDraftSaving] = useState(false)

  // 언마운트 시 남은 Object URL 해제
  useEffect(() => {
    return () => { previewsRef.current.forEach(URL.revokeObjectURL) }
  }, [])

  // 마운트 시 임시저장 로드 (비인증 사용자 401 등 모든 에러 무음 처리)
  useEffect(() => {
    postsApi.getDraft()
      .then((draft) => { if (draft) setDraftDialog(draft) })
      .catch(() => {})
  }, [])

  const updatePreviews = (files: File[]) => {
    previewsRef.current.forEach(URL.revokeObjectURL)
    const next = files.map((f) => URL.createObjectURL(f))
    previewsRef.current = next
    setPreviews(next)
  }

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(''), 2500)
  }

  const restoreDraft = (draft: DraftResponse) => {
    setTitle(draft.title)
    setDescription(draft.description)
    setIsFree(draft.is_free)
    setPrice(draft.price != null ? String(draft.price) : '')
    setTradePlace(draft.trade_place ?? '')
    setDraftDialog(null)
    showToast('임시저장 내용을 복원했어요. 사진은 다시 선택해주세요.')
  }

  const getCurrentDraftPayload = () => {
    const parsedPrice = parseInt(price, 10)
    return {
      title,
      description,
      price: isFree ? null : (price.trim() && !Number.isNaN(parsedPrice) ? parsedPrice : null),
      is_free: isFree,
      trade_place: tradePlace.trim() || null,
      photos: [] as string[],
    }
  }

  const handleSaveDraft = async () => {
    setDraftSaving(true)
    try {
      await postsApi.saveDraft(getCurrentDraftPayload())
      showToast('임시저장됐어요!')
    } catch {
      showToast('임시저장에 실패했습니다.')
    } finally {
      setDraftSaving(false)
    }
  }

  const handleBack = () => setShowBackDialog(true)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    setFileError('')

    const oversized = files.filter((f) => f.size > MAX_FILE_SIZE)
    if (oversized.length > 0) {
      setFileError(`5MB를 초과하는 파일: ${oversized.map((f) => f.name).join(', ')}`)
      e.target.value = ''
      return
    }

    const combined = [...selectedFiles, ...files].slice(0, MAX_PHOTOS)
    setSelectedFiles(combined)
    updatePreviews(combined)
    e.target.value = ''
  }

  const removePhoto = (index: number) => {
    const next = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(next)
    updatePreviews(next)
  }

  const uploadFile = async (file: File): Promise<string> => {
    const { upload_url, file_path } = await postsApi.getUploadUrl()
    const res = await fetch(upload_url, {
      method: 'PUT',
      body: file,
      headers: { 'Content-Type': file.type || 'image/jpeg' },
    })
    if (!res.ok) throw new Error(`이미지 업로드 실패 (${res.status})`)
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
    return `${supabaseUrl}/storage/v1/object/public/posts/${file_path}`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (selectedFiles.length === 0) {
      setError('사진을 1장 이상 선택해주세요.')
      return
    }
    if (!title.trim()) {
      setError('제목을 입력해주세요.')
      return
    }
    if (!description.trim()) {
      setError('설명을 입력해주세요.')
      return
    }

    setLoading(true)
    try {
      const photoUrls = await Promise.all(selectedFiles.map(uploadFile))

      await postsApi.createPost({
        title: title.trim(),
        description: description.trim(),
        price: isFree ? null : price ? parseInt(price, 10) : null,
        is_free: isFree,
        trade_place: tradePlace.trim() || null,
        photos: photoUrls,
      })

      showToast('등록됐어요!')
      router.push('/')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: unknown } } }
      const detail = axiosErr.response?.data?.detail
      if (typeof detail === 'string') {
        setError(detail)
      } else {
        setError('게시글 등록에 실패했습니다.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white max-w-lg mx-auto">
      {loading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/80 gap-3">
          <div className="w-10 h-10 border-4 border-orange-400 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-gray-500">등록 중...</p>
        </div>
      )}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-gray-800 text-white text-sm px-5 py-2.5 rounded-full shadow-lg">
          {toast}
        </div>
      )}

      {/* 임시저장 복원 다이얼로그 */}
      {draftDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl p-6 mx-4 shadow-xl max-w-sm w-full">
            <h2 className="font-semibold text-base mb-2">이전에 작성 중인 글이 있어요</h2>
            <p className="text-sm text-gray-500 mb-5">이어서 작성하시겠어요?</p>
            <div className="flex gap-2">
              <button
                onClick={() => setDraftDialog(null)}
                className="flex-1 py-2.5 rounded-lg border text-sm text-gray-600"
              >
                새로 작성
              </button>
              <button
                onClick={() => restoreDraft(draftDialog)}
                className="flex-1 py-2.5 rounded-lg text-sm text-white font-medium"
                style={{ backgroundColor: '#FF7E36' }}
              >
                이어서 작성
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 뒤로가기 다이얼로그 */}
      {showBackDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl p-6 mx-4 shadow-xl max-w-sm w-full">
            <h2 className="font-semibold text-base mb-2">작성 중인 글이 있어요</h2>
            <p className="text-sm text-gray-500 mb-5">임시저장할까요?</p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowBackDialog(false)}
                className="flex-1 py-2.5 rounded-lg border text-sm text-gray-600"
              >
                취소
              </button>
              <button
                onClick={() => { setShowBackDialog(false); router.back() }}
                className="flex-1 py-2.5 rounded-lg border text-sm text-gray-600"
              >
                저장 안 함
              </button>
              <button
                onClick={async () => {
                  try {
                    await postsApi.saveDraft(getCurrentDraftPayload())
                    showToast('임시저장됐어요!')
                    setShowBackDialog(false)
                    router.back()
                  } catch {
                    showToast('임시저장에 실패했습니다.')
                    // 저장 실패 시 다이얼로그 유지 — 사용자가 재시도 가능
                  }
                }}
                className="flex-1 py-2.5 rounded-lg text-sm text-white font-medium"
                style={{ backgroundColor: '#FF7E36' }}
              >
                저장 후 나가기
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3 flex items-center justify-between">
        <button onClick={handleBack} className="text-gray-600">← 뒤로</button>
        <h1 className="font-semibold">내 물건 팔기</h1>
        <button
          type="button"
          onClick={handleSaveDraft}
          disabled={draftSaving || loading}
          className="text-sm text-gray-500 disabled:opacity-40"
        >
          임시저장
        </button>
      </header>

      <form onSubmit={handleSubmit} className="p-4 space-y-5">
        {/* 사진 선택 */}
        <div>
          <div className="flex gap-2 flex-wrap">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-20 h-20 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center text-gray-400 text-xs"
            >
              📷<br />{selectedFiles.length}/{MAX_PHOTOS}
            </button>
            {previews.map((src, i) => (
              <div key={src} className="relative w-20 h-20">
                <Image src={src} alt="" fill className="object-cover rounded-xl" sizes="80px" />
                <button
                  type="button"
                  onClick={() => removePhoto(i)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-gray-700 text-white rounded-full text-xs flex items-center justify-center"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
          {fileError && <p className="text-red-500 text-xs mt-1">{fileError}</p>}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>

        {/* 제목 */}
        <div className="space-y-1">
          <Label htmlFor="title">제목</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={100}
            placeholder="글 제목"
            disabled={loading}
          />
        </div>

        {/* 가격 / 나눔 */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="isFree"
              checked={isFree}
              onChange={(e) => setIsFree(e.target.checked)}
              className="w-4 h-4"
            />
            <Label htmlFor="isFree">나눔하기</Label>
          </div>
          {!isFree && (
            <Input
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="가격 (원)"
              min={0}
              disabled={loading}
            />
          )}
        </div>

        {/* 설명 */}
        <div className="space-y-1">
          <Label htmlFor="description">자세한 설명</Label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
            placeholder="물품에 대해 자세히 설명해주세요."
            className="w-full border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-orange-400"
            disabled={loading}
          />
        </div>

        {/* 거래 희망 장소 */}
        <div className="space-y-1">
          <Label htmlFor="tradePlace">거래 희망 장소 (선택)</Label>
          <Input
            id="tradePlace"
            value={tradePlace}
            onChange={(e) => setTradePlace(e.target.value)}
            placeholder="예: 강남역 2번 출구"
            disabled={loading}
          />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <Button
          type="submit"
          className="w-full"
          style={{ backgroundColor: '#FF7E36' }}
          disabled={loading}
        >
          {loading ? '등록 중...' : '작성 완료'}
        </Button>
      </form>
    </div>
  )
}
