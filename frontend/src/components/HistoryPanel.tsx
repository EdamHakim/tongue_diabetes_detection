import { useEffect, useState } from 'react'
import { fetchHistory } from '../lib/api'
import type { HistoryItem } from '../lib/types'
import { RiskBadge } from './RiskBadge'

function fmt(dt: string) {
  const d = new Date(dt)
  return d.toLocaleString()
}

export function HistoryPanel({
  patientId,
  onOpen,
}: {
  patientId: string
  onOpen: (item: HistoryItem) => void
}) {
  const [items, setItems] = useState<HistoryItem[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!patientId) return
    setLoading(true)
    setError(null)
    fetchHistory(patientId)
      .then((r) => setItems(r.items))
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Failed to load history'))
      .finally(() => setLoading(false))
  }, [patientId])

  return (
    <section className="rounded-xl border border-clinical-border bg-white p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-clinical-text">History</h3>
          <p className="text-xs text-clinical-muted">Last 50 analyses for this patient ID</p>
        </div>
      </div>

      <div className="mt-3">
        {loading && <div className="text-sm text-clinical-muted">Loading…</div>}
        {error && <div className="text-sm text-clinical-danger">{error}</div>}
        {!loading && !error && (items?.length ?? 0) === 0 && (
          <div className="text-sm text-clinical-muted">No prior analyses found.</div>
        )}

        <ul className="mt-2 space-y-2">
          {(items || []).map((it) => (
            <li key={it.analysis_id}>
              <button
                type="button"
                onClick={() => onOpen(it)}
                className="w-full rounded-lg border border-clinical-border bg-clinical-bg px-3 py-2 text-left transition hover:bg-white"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium text-clinical-text">
                      #{it.analysis_id} · {fmt(it.created_at)}
                    </div>
                    <div className="text-xs text-clinical-muted">
                      p(diabetes) {(it.probability_diabetes * 100).toFixed(1)}%
                    </div>
                  </div>
                  <RiskBadge risk={it.risk_band} />
                </div>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}

