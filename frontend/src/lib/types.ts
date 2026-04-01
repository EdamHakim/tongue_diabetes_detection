export type RiskBand = 'low' | 'moderate' | 'high'

export type AnalyzeResponse = {
  analysis_id: number
  created_at: string
  patient_id: string
  prediction: 'diabetes' | 'nondiabetes' | string
  risk_band: RiskBand | string
  probability_diabetes: number
  confidence_pct: number
  clinical_note: string
  original_image_url: string
  xai_overlay_url: string
  xai_legend: {
    type: string
    meaning: string
    low_label: string
    high_label: string
    colormap: string
    alpha: number
  }
}

export type HistoryItem = {
  analysis_id: number
  created_at: string
  prediction: string
  risk_band: string
  probability_diabetes: number
  original_image_url: string
  xai_overlay_url: string
}

export type HistoryResponse = {
  patient_id: string
  items: HistoryItem[]
}

export type ApiError = {
  detail?: string
}

