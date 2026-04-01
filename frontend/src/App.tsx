import { Navigate, Route, Routes } from 'react-router-dom'
import { ResultsPage } from './pages/ResultsPage'
import { UploadPage } from './pages/UploadPage'

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-clinical-border bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <div>
            <div className="text-sm font-semibold text-clinical-text">Glunova</div>
            <div className="text-xs text-clinical-muted">Diabetic tongue detection (t2d_tongue_detection)</div>
          </div>
          <div className="text-xs text-clinical-muted">Clinical screening UI</div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/results/:id" element={<ResultsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="border-t border-clinical-border bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-clinical-muted">
          This application provides decision support only and does not replace clinical judgment.
        </div>
      </footer>
    </div>
  )
}
