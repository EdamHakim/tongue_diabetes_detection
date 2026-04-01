import { useLocation, useNavigate, useParams } from 'react-router-dom'
import type { AnalyzeResponse } from '../lib/types'
import { RiskBadge } from '../components/RiskBadge'
import { ImageCompare } from '../components/ImageCompare'

function loadFromStorage(id: string | undefined): AnalyzeResponse | null {
  if (!id) return null
  const raw = sessionStorage.getItem(`analysis:${id}`)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AnalyzeResponse
  } catch {
    return null
  }
}

export function ResultsPage() {
  const nav = useNavigate()
  const { id } = useParams()
  const loc = useLocation()
  const state = loc.state as AnalyzeResponse | null
  const r = state || loadFromStorage(id)

  if (!r) {
    return (
      <div className="rounded-xl border border-clinical-border bg-white p-5">
        <h2 className="text-lg font-semibold text-clinical-text">Result not found</h2>
        <p className="mt-1 text-sm text-clinical-muted">
          This page needs a recent analysis. Please go back and run a new upload.
        </p>
        <button
          type="button"
          className="mt-4 rounded-lg bg-clinical-primary px-4 py-2 text-sm font-semibold text-white"
          onClick={() => nav('/')}
        >
          Back to upload
        </button>
      </div>
    )
  }

  const probPct = (r.probability_diabetes * 100).toFixed(1)

  return (
    <div className="space-y-4">
      <section className="rounded-xl border border-clinical-border bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-clinical-text">Results</h2>
            <p className="mt-1 text-sm text-clinical-muted">
              Patient <span className="font-medium text-clinical-text">{r.patient_id}</span> · Analysis #
              {r.analysis_id}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <RiskBadge risk={r.risk_band} />
            <div className="rounded-lg border border-clinical-border bg-clinical-bg px-3 py-2 text-sm text-clinical-text">
              <div className="text-xs text-clinical-muted">p(diabetes)</div>
              <div className="font-semibold">{probPct}%</div>
            </div>
            <div className="rounded-lg border border-clinical-border bg-clinical-bg px-3 py-2 text-sm text-clinical-text">
              <div className="text-xs text-clinical-muted">confidence</div>
              <div className="font-semibold">{r.confidence_pct.toFixed(1)}%</div>
            </div>
          </div>
        </div>

        <div className="mt-4">
          <ImageCompare
            leftTitle="Original image"
            rightTitle="XAI overlay (suspicious regions)"
            leftSrc={r.original_image_url}
            rightSrc={r.xai_overlay_url}
          />
        </div>

        <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_360px]">
          <div className="rounded-xl border border-clinical-border bg-clinical-bg p-4">
            <h3 className="text-sm font-semibold text-clinical-text">Clinical note</h3>
            <p className="mt-2 text-sm text-clinical-muted">
              {r.clinical_note ||
                'This result is stored from history. Run a fresh analysis to generate a full clinical note.'}
            </p>
          </div>

          <div className="rounded-xl border border-clinical-border bg-clinical-bg p-4">
            <h3 className="text-sm font-semibold text-clinical-text">Heatmap legend</h3>
            <p className="mt-2 text-xs text-clinical-muted">{r.xai_legend.meaning}</p>
            <div className="mt-3">
              <div className="flex items-center justify-between text-[11px] text-clinical-muted">
                <span>{r.xai_legend.low_label}</span>
                <span>{r.xai_legend.high_label}</span>
              </div>
              <div className="mt-1 h-3 w-full rounded bg-gradient-to-r from-blue-600 via-yellow-400 to-red-600" />
              <div className="mt-2 text-[11px] text-clinical-muted">
                Overlay opacity (alpha): {r.xai_legend.alpha}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            type="button"
            className="rounded-lg border border-clinical-border bg-white px-3 py-2 text-sm font-medium text-clinical-text hover:bg-clinical-bg"
            onClick={() => nav('/')}
          >
            New analysis
          </button>
        </div>
      </section>
    </div>
  )
}

