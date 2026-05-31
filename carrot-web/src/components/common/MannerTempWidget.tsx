interface Props {
  temp: number
}

function getTempColor(temp: number): string {
  if (temp <= 30) return '#3B82F6'   // 파랑 (낮은 신뢰도)
  if (temp <= 50) return '#FF7E36'   // 오렌지 (좋음)
  return '#EF4444'                    // 빨강 (매우 높음)
}

export function MannerTempWidget({ temp }: Props) {
  return (
    <span
      className="inline-flex items-center gap-1 font-semibold text-lg"
      style={{ color: getTempColor(temp) }}
      aria-label={`매너온도 ${temp.toFixed(1)}도`}
    >
      🥕 {temp.toFixed(1)}℃
    </span>
  )
}
