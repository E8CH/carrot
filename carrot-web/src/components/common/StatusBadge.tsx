const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  '예약중': { label: '예약중', className: 'bg-[#6B7280] text-white' },
  '거래완료': { label: '거래완료', className: 'bg-[#374151] text-white' },
}

interface Props {
  status: string
}

export function StatusBadge({ status }: Props) {
  const config = STATUS_CONFIG[status]
  if (!config) return null  // 판매중은 배지 없음

  return (
    <span className={`inline-block text-xs font-medium px-1.5 py-0.5 rounded ${config.className}`}>
      {config.label}
    </span>
  )
}
