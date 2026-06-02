'use client'

import { useEffect, useRef, useState } from 'react'
import { ragApi } from '@/lib/api/rag'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export function ChatBot() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: '안녕하세요! carrot 도움말 챗봇입니다. 궁금한 점을 물어보세요 😊' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await ragApi.chat(text)
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer }])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: '죄송합니다. 잠시 후 다시 시도해주세요.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* 채팅 패널 */}
      {open && (
        <div className="fixed bottom-20 right-4 z-50 w-80 h-[460px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col overflow-hidden">
          {/* 헤더 */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100" style={{ backgroundColor: '#FF7E36' }}>
            <div className="flex items-center gap-2">
              <span className="text-white text-lg">🥕</span>
              <span className="text-white font-semibold text-sm">carrot 도움말</span>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-white/80 hover:text-white text-lg leading-none"
            >
              ✕
            </button>
          </div>

          {/* 메시지 목록 */}
          <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'text-white rounded-br-sm'
                      : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                  }`}
                  style={msg.role === 'user' ? { backgroundColor: '#FF7E36' } : {}}
                >
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 px-3 py-2 rounded-2xl rounded-bl-sm">
                  <div className="flex gap-1 items-center h-5">
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                    <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* 입력창 */}
          <div className="px-3 py-2 border-t border-gray-100 flex gap-2">
            <input
              className="flex-1 text-sm border border-gray-200 rounded-full px-3 py-1.5 outline-none focus:border-orange-400"
              placeholder="질문을 입력하세요..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              disabled={loading}
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              className="w-8 h-8 rounded-full flex items-center justify-center text-white disabled:opacity-40 transition-opacity"
              style={{ backgroundColor: '#FF7E36' }}
            >
              ↑
            </button>
          </div>
        </div>
      )}

      {/* 플로팅 버튼 */}
      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-4 right-4 z-50 w-12 h-12 rounded-full shadow-lg flex items-center justify-center text-white text-xl transition-transform hover:scale-105"
        style={{ backgroundColor: '#FF7E36' }}
        aria-label="도움말 챗봇"
      >
        {open ? '✕' : '💬'}
      </button>
    </>
  )
}
