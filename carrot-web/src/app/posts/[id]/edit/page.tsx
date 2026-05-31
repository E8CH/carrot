'use client'

import { useEffect, useRef, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { useQuery } from '@tanstack/react-query'
import { postsApi } from '@/lib/api/posts'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const MAX_FILE_SIZE = 5 * 1024 * 1024
const MAX_PHOTOS = 10

export default function EditPostPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const postId = Number(id)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const previewsRef = useRef<string[]>([])

  const { data: post, isLoading, isError } = useQuery({
    queryKey: ['post', postId],
    queryFn: () => postsApi.getPost(postId),
    enabled: !Number.isNaN(postId),
  })

  const [existingPhotos, setExistingPhotos] = useState<string[]>([])
  const [newFiles, setNewFiles] = useState<File[]>([])
  const [newPreviews, setNewPreviews] = useState<string[]>([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [isFree, setIsFree] = useState(false)
  const [tradePlace, setTradePlace] = useState('')
  const [error, setError] = useState('')
  const [fileError, setFileError] = useState('')
  const [loading, setLoading] = useState(false)
  const [initialized, setInitialized] = useState(false)

  // 기존 데이터 pre-populate (1회)
  useEffect(() => {
    if (post && !initialized) {
      setTitle(post.title)
      setDescription(post.description)
      setIsFree(post.is_free)
      setPrice(post.price != null ? String(post.price) : '')
      setTradePlace(post.trade_place ?? '')
      setExistingPhotos(post.photos)
      setInitialized(true)
    }
  }, [post, initialized])

  // 언마운트 시 Object URL 해제
  useEffect(() => {
    return () => { previewsRef.current.forEach(URL.revokeObjectURL) }
  }, [])

  const removeExistingPhoto = (url: string) => {
    setExistingPhotos((prev) => prev.filter((u) => u !== url))
  }

  const removeNewPhoto = (index: number) => {
    URL.revokeObjectURL(previewsRef.current[index])
    const nextFiles = newFiles.filter((_, i) => i !== index)
    const nextPreviews = previewsRef.current.filter((_, i) => i !== index)
    previewsRef.current = nextPreviews
    setNewFiles(nextFiles)
    setNewPreviews(nextPreviews)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? [])
    setFileError('')

    const oversized = files.filter((f) => f.size > MAX_FILE_SIZE)
    if (oversized.length > 0) {
      setFileError(`5MB를 초과하는 파일: ${oversized.map((f) => f.name).join(', ')}`)
      e.target.value = ''
      return
    }

    const totalCount = existingPhotos.length + newFiles.length + files.length
    if (totalCount > MAX_PHOTOS) {
      setFileError(`사진은 최대 ${MAX_PHOTOS}장까지 선택할 수 있습니다.`)
      e.target.value = ''
      return
    }

    const combined = [...newFiles, ...files]
    previewsRef.current.forEach(URL.revokeObjectURL)
    const previews = combined.map((f) => URL.createObjectURL(f))
    previewsRef.current = previews
    setNewFiles(combined)
    setNewPreviews(previews)
    e.target.value = ''
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

    if (existingPhotos.length + newFiles.length === 0) {
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
      const uploadedUrls = await Promise.all(newFiles.map(uploadFile))
      const photos = [...existingPhotos, ...uploadedUrls]
      const parsedPrice = parseInt(price, 10)

      await postsApi.updatePost(postId, {
        title: title.trim(),
        description: description.trim(),
        price: isFree ? null : (price.trim() && !Number.isNaN(parsedPrice) ? parsedPrice : null),
        is_free: isFree,
        trade_place: tradePlace.trim() || null,
        photos,
      })

      router.push(`/posts/${postId}`)
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: unknown } } }
      const detail = axiosErr.response?.data?.detail
      setError(typeof detail === 'string' ? detail : '수정에 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  if (isError) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">게시글을 불러올 수 없습니다.</div>
  }
  if (isLoading || !initialized) {
    return <div className="min-h-screen flex items-center justify-center text-gray-400">불러오는 중...</div>
  }

  const totalCount = existingPhotos.length + newFiles.length

  return (
    <div className="min-h-screen bg-white max-w-4xl mx-auto">
      <header className="sticky top-0 z-10 bg-white border-b px-4 py-3 flex items-center justify-between">
        <button onClick={() => router.back()} className="text-gray-600">← 뒤로</button>
        <h1 className="font-semibold">게시글 수정</h1>
        <div />
      </header>

      <form onSubmit={handleSubmit} className="p-4 space-y-5">
        {/* 사진 */}
        <div>
          <div className="flex gap-2 flex-wrap">
            {existingPhotos.map((url) => (
              <div key={url} className="relative w-20 h-20">
                <Image src={url} alt="" fill className="object-cover rounded-xl" sizes="80px" />
                <button
                  type="button"
                  onClick={() => removeExistingPhoto(url)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-gray-700 text-white rounded-full text-xs flex items-center justify-center"
                >×</button>
              </div>
            ))}
            {newPreviews.map((src, i) => (
              <div key={src} className="relative w-20 h-20">
                <Image src={src} alt="" fill className="object-cover rounded-xl" sizes="80px" />
                <button
                  type="button"
                  onClick={() => removeNewPhoto(i)}
                  className="absolute -top-1 -right-1 w-5 h-5 bg-orange-500 text-white rounded-full text-xs flex items-center justify-center"
                >×</button>
              </div>
            ))}
            {totalCount < MAX_PHOTOS && (
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-20 h-20 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center text-gray-400 text-xs"
              >
                📷<br />{totalCount}/{MAX_PHOTOS}
              </button>
            )}
          </div>
          {fileError && <p className="text-red-500 text-xs mt-1">{fileError}</p>}
          <input ref={fileInputRef} type="file" accept="image/*" multiple className="hidden" onChange={handleFileSelect} />
        </div>

        <div className="space-y-1">
          <Label htmlFor="title">제목</Label>
          <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={100} disabled={loading} />
        </div>

        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <input type="checkbox" id="isFree" checked={isFree} onChange={(e) => setIsFree(e.target.checked)} className="w-4 h-4" />
            <Label htmlFor="isFree">나눔하기</Label>
          </div>
          {!isFree && (
            <Input type="number" value={price} onChange={(e) => setPrice(e.target.value)} placeholder="가격 (원)" min={0} disabled={loading} />
          )}
        </div>

        <div className="space-y-1">
          <Label htmlFor="description">자세한 설명</Label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={5}
            className="w-full border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-orange-400"
            disabled={loading}
          />
        </div>

        <div className="space-y-1">
          <Label htmlFor="tradePlace">거래 희망 장소 (선택)</Label>
          <Input id="tradePlace" value={tradePlace} onChange={(e) => setTradePlace(e.target.value)} placeholder="예: 강남역 2번 출구" disabled={loading} />
        </div>

        {error && <p className="text-red-500 text-sm">{error}</p>}

        <Button type="submit" className="w-full" style={{ backgroundColor: '#FF7E36' }} disabled={loading}>
          {loading ? '저장 중...' : '수정 완료'}
        </Button>
      </form>
    </div>
  )
}
