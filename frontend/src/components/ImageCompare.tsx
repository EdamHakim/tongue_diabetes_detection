type Props = {
  leftTitle: string
  rightTitle: string
  leftSrc: string
  rightSrc: string
}

export function ImageCompare({ leftTitle, rightTitle, leftSrc, rightSrc }: Props) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <figure className="rounded-xl border border-clinical-border bg-white p-3">
        <figcaption className="mb-2 text-sm font-medium text-clinical-text">{leftTitle}</figcaption>
        <img
          src={leftSrc}
          alt={leftTitle}
          className="h-auto w-full rounded-lg border border-clinical-border object-contain"
        />
      </figure>

      <figure className="rounded-xl border border-clinical-border bg-white p-3">
        <figcaption className="mb-2 text-sm font-medium text-clinical-text">{rightTitle}</figcaption>
        <img
          src={rightSrc}
          alt={rightTitle}
          className="h-auto w-full rounded-lg border border-clinical-border object-contain"
        />
      </figure>
    </div>
  )
}

