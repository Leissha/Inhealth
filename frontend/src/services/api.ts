import type { MetricName, ReadingHistoryResponse, ReadingStatsResponse, SensorReading } from '../types/reading'
import type { ActuatorAlertResponse, DeviceStatus, SystemSettings } from '../types/settings'
import type { SummaryResponse } from '../types/summary'

const API_ROOT = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers: HeadersInit = {
    Accept: 'application/json',
    ...(options?.body ? { 'Content-Type': 'application/json' } : {}),
    ...options?.headers,
  }

  const response = await fetch(`${API_ROOT}${path}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    let errorMessage = 'The edge API could not be reached. Check that FastAPI is running.'
    try {
      const errorJson = await response.json()
      if (errorJson.detail) {
        errorMessage = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail)
      }
    } catch {
      if (response.status === 404) {
        errorMessage = 'Requested resource not found.'
      }
    }
    throw new Error(errorMessage)
  }

  return response.json() as Promise<T>
}

export const readingsApi = {
  getLatest: () => request<SensorReading>('/api/readings/latest'),
  getHistory(metric: MetricName = 'tvoc', rangeHours = 24, limit = 200) {
    const params = new URLSearchParams({ metric, range: String(rangeHours), limit: String(limit) })
    return request<ReadingHistoryResponse>(`/api/readings/history?${params}`)
  },
  getStats(metric: MetricName = 'tvoc', rangeHours = 24) {
    const params = new URLSearchParams({ metric, range: String(rangeHours) })
    return request<ReadingStatsResponse>(`/api/readings/stats?${params}`)
  },
}

export const settingsApi = {
  getSettings: () => request<SystemSettings>('/api/settings'),
  updateTvocThreshold: (value: number) =>
    request<SystemSettings>('/api/settings/tvoc-threshold', {
      method: 'PUT',
      body: JSON.stringify({ value }),
    }),
}

export const actuatorsApi = {
  setAlert: (enabled: boolean) =>
    request<ActuatorAlertResponse>('/api/actuators/alert', {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    }),
}

export const deviceApi = {
  getStatus: () => request<DeviceStatus>('/api/device/status'),
}

export const summaryApi = {
  generate: (rangeHours: number) =>
    request<SummaryResponse>('/api/summary', {
      method: 'POST',
      body: JSON.stringify({ range_hours: rangeHours }),
    }),
}
