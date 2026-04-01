import type { RiskBand } from '../lib/types'

function clsx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export function RiskBadge({ risk }: { risk: RiskBand | string }) {
  const base =
    'inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold tracking-wide uppercase'

  const style =
    risk === 'low'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-800'
      : risk === 'moderate'
        ? 'border-amber-200 bg-amber-50 text-amber-800'
        : risk === 'high'
          ? 'border-red-200 bg-red-50 text-red-800'
          : 'border-gray-200 bg-gray-50 text-gray-700'

  return <span className={clsx(base, style)}>{risk}</span>
}

