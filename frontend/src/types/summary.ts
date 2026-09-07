export interface SummaryResponse {
  range_hours: number
  summary: string
  sample_count: number
  generated_at: string
  alerts: { automatic_on_count: number; manual_on_count: number }
  outdoor: { available: boolean; source: string; location: string }
}
