import { useCallback, useMemo, useRef, useState } from 'react'

type Props = {
  label: string
  accept?: string
  onFileSelected: (file: File) => void
  disabled?: boolean
}

function clsx(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(' ')
}

export function Dropzone({ label, accept = 'image/*', onFileSelected, disabled }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const [isDragging, setIsDragging] = useState(false)

  const helpText = useMemo(() => 'PNG, JPG, or WebP. Clear tongue visibility is recommended.', [])

  const pick = useCallback(() => {
    if (disabled) return
    inputRef.current?.click()
  }, [disabled])

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      if (disabled) return
      setIsDragging(false)
      const file = e.dataTransfer.files?.[0]
      if (file) onFileSelected(file)
    },
    [disabled, onFileSelected],
  )

  return (
    <div>
      <div className="flex items-baseline justify-between">
        <label className="text-sm font-medium text-clinical-text">{label}</label>
        <span className="text-xs text-clinical-muted">{helpText}</span>
      </div>

      <div
        className={clsx(
          'mt-2 rounded-xl border border-dashed bg-white p-6 transition',
          disabled && 'opacity-60',
          isDragging ? 'border-clinical-primary bg-emerald-50/40' : 'border-clinical-border',
        )}
        role="button"
        tabIndex={0}
        aria-disabled={disabled ? 'true' : 'false'}
        onClick={pick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') pick()
        }}
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
      >
        <div className="text-center">
          <div className="text-sm text-clinical-text">
            <span className="font-semibold">Drag & drop</span> an image here, or{' '}
            <span className="font-semibold text-clinical-primary">browse</span>
          </div>
          <div className="mt-1 text-xs text-clinical-muted">The image is processed on your server.</div>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          disabled={disabled}
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onFileSelected(file)
          }}
        />
      </div>
    </div>
  )
}

