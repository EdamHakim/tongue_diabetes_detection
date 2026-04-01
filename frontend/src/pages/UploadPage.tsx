import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeTongue } from '../lib/api'
import type { AnalyzeResponse, HistoryItem } from '../lib/types'
import { Dropzone } from '../components/Dropzone'
import { HistoryPanel } from '../components/HistoryPanel'

function isSupported(file: File) {
  return ['image/jpeg', 'image/png', 'image/webp'].includes(file.type)
}

function saveResult(r: AnalyzeResponse) {
  sessionStorage.setItem(`analysis:${r.analysis_id}`, JSON.stringify(r))
}

export function UploadPage() {
  const nav = useNavigate()
  const [patientId, setPatientId] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canSubmit = useMemo(() => !!patientId.trim() && !!file && isSupported(file) && !busy, [patientId, file, busy])

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <section className="rounded-xl border border-clinical-border bg-white p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-lg font-semibold text-clinical-text">Tongue screening upload</h2>
            <p className="mt-1 text-sm text-clinical-muted">
              Upload a tongue image to estimate diabetes risk and view an explanation overlay.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4">
          <div>
            <label className="text-sm font-medium text-clinical-text">Patient ID</label>
            <input
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              placeholder="e.g., P-000142"
              className="mt-2 w-full rounded-lg border border-clinical-border bg-white px-3 py-2 text-sm text-clinical-text shadow-sm"
            />
            <p className="mt-1 text-xs text-clinical-muted">Used to group results in the History panel.</p>
          </div>

          <Dropzone
            label="Tongue image"
            disabled={busy}
            onFileSelected={(f) => {
              setError(null)
              setFile(f)
              setPreviewUrl(URL.createObjectURL(f))
            }}
          />

          {file && !isSupported(file) && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">
              Unsupported file type. Please upload PNG, JPG, or WebP.
            </div>
          )}

          {previewUrl && (
            <div className="rounded-xl border border-clinical-border bg-clinical-bg p-3">
              <div className="mb-2 text-xs font-medium text-clinical-muted">Preview</div>
              <img
                src={previewUrl}
                alt="Selected upload preview"
                className="max-h-[420px] w-full rounded-lg border border-clinical-border object-contain"
              />
            </div>
          )}

          {error && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</div>
          )}

          <div className="flex items-center justify-end gap-3">
            <button
              type="button"
              className="rounded-lg border border-clinical-border bg-white px-3 py-2 text-sm font-medium text-clinical-text hover:bg-clinical-bg disabled:opacity-60"
              onClick={() => {
                setFile(null)
                setPreviewUrl(null)
                setError(null)
              }}
              disabled={busy}
            >
              Clear
            </button>
            <button
              type="button"
              className="rounded-lg bg-clinical-primary px-4 py-2 text-sm font-semibold text-white shadow-sm hover:opacity-95 disabled:opacity-60"
              disabled={!canSubmit}
              onClick={async () => {
                if (!file) return
                setBusy(true)
                setError(null)
                try {
                  const r = await analyzeTongue({ patientId, file })
                  saveResult(r)
                  nav(`/results/${r.analysis_id}`, { state: r })
                } catch (e: unknown) {
                  setError(e instanceof Error ? e.message : 'Analysis failed')
                } finally {
                  setBusy(false)
                }
              }}
            >
              {busy ? 'Analyzing…' : 'Analyze'}
            </button>
          </div>
        </div>
      </section>

      <aside className="space-y-4">
        <div className="rounded-xl border border-clinical-border bg-white p-4">
          <h3 className="text-sm font-semibold text-clinical-text">Clinical guidance</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-clinical-muted">
            <li>Ensure the tongue is centered and well-lit.</li>
            <li>Avoid heavy filters, blur, and extreme compression.</li>
            <li>This is a screening tool, not a definitive diagnosis.</li>
          </ul>
        </div>

        {!!patientId.trim() && (
          <HistoryPanel
            patientId={patientId.trim()}
            onOpen={(it: HistoryItem) => {
              const r: AnalyzeResponse = {
                analysis_id: it.analysis_id,
                created_at: it.created_at,
                patient_id: patientId.trim(),
                prediction: it.prediction,
                risk_band: it.risk_band,
                probability_diabetes: it.probability_diabetes,
                confidence_pct: Math.max(it.probability_diabetes, 1 - it.probability_diabetes) * 100,
                clinical_note: '',
                original_image_url: it.original_image_url,
                xai_overlay_url: it.xai_overlay_url,
                xai_legend: {
                  type: 'heatmap_overlay',
                  meaning: 'Warmer colors indicate higher influence.',
                  low_label: 'Lower influence',
                  high_label: 'Higher influence',
                  colormap: 'jet',
                  alpha: 0.5,
                },
              }
              saveResult(r)
              nav(`/results/${it.analysis_id}`, { state: r })
            }}
          />
        )}
      </aside>
    </div>
  )
}

