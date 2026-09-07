export type MetricName = 'temp_analog_c' | 'temp_digital_c' | 'humidity' | 'aqi' | 'tvoc' | 'eco2' | 'pm1' | 'pm25' | 'pm10'

export interface SensorReading {
  id: number
  recorded_at: string
  temp_analog_c: number | null
  temp_digital_c: number | null
  humidity: number | null
  aqi: number | null
  tvoc: number | null
  eco2: number | null
  pm1: number | null
  pm25: number | null
  pm10: number | null
}

export interface HistoryPoint { recorded_at: string; value: number }
export interface ReadingHistoryResponse { metric: MetricName; points: HistoryPoint[] }

export interface ReadingStatsResponse {
  metric: MetricName
  range: number
  count: number
  minimum: number | null
  average: number | null
  maximum: number | null
}
