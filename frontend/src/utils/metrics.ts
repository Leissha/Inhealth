import type { Component } from 'vue'
import { Activity, Cloud, Droplets, Gauge, Thermometer, Wind } from '@lucide/vue'
import type { MetricName, SensorReading } from '../types/reading'

export type StatusTone = 'healthy' | 'warning' | 'alert' | 'neutral'
export interface MetricDefinition { key: MetricName; label: string; unit: string; icon: Component; decimals?: number; chartToken: string }

export const metricDefinitions: Record<MetricName, MetricDefinition> = {
  temp_digital_c: { key: 'temp_digital_c', label: 'Digital temperature', unit: '°C', icon: Thermometer, decimals: 1, chartToken: '--chart-primary' },
  temp_analog_c: { key: 'temp_analog_c', label: 'Analog temperature', unit: '°C', icon: Thermometer, decimals: 1, chartToken: '--chart-primary' },
  humidity: { key: 'humidity', label: 'Humidity', unit: '%', icon: Droplets, decimals: 1, chartToken: '--chart-secondary' },
  aqi: { key: 'aqi', label: 'Air quality index', unit: '', icon: Activity, chartToken: '--success' },
  tvoc: { key: 'tvoc', label: 'TVOC', unit: 'ppb', icon: Cloud, chartToken: '--warning' },
  eco2: { key: 'eco2', label: 'eCO₂', unit: 'ppm', icon: Gauge, chartToken: '--primary' },
  pm1: { key: 'pm1', label: 'PM1', unit: 'µg/m³', icon: Wind, decimals: 1, chartToken: '--danger' },
  pm25: { key: 'pm25', label: 'PM2.5', unit: 'µg/m³', icon: Wind, decimals: 1, chartToken: '--danger' },
  pm10: { key: 'pm10', label: 'PM10', unit: 'µg/m³', icon: Wind, decimals: 1, chartToken: '--danger' },
}

export const primaryMetrics: MetricDefinition[] = [
  metricDefinitions.temp_digital_c, metricDefinitions.humidity, metricDefinitions.aqi,
  metricDefinitions.pm25, metricDefinitions.tvoc, metricDefinitions.eco2,
]
export const secondaryMetrics: MetricDefinition[] = [
  metricDefinitions.temp_analog_c, metricDefinitions.pm1, metricDefinitions.pm10,
]

export const analyticsMetrics = Object.values(metricDefinitions)

export function isMetricName(value: unknown): value is MetricName {
  return typeof value === 'string' && value in metricDefinitions
}

export function formatValue(value: number | null, metric: MetricDefinition): string {
  if (value === null) return '—'
  return metric.decimals === undefined ? String(value) : value.toFixed(metric.decimals)
}

export const statusToneClasses: Record<StatusTone, { badge: string; icon: string; border: string }> = {
  healthy: { badge: 'bg-success/10 text-success', icon: 'bg-success/10 text-success', border: 'border-success/20' },
  warning: { badge: 'bg-warning/10 text-warning', icon: 'bg-warning/10 text-warning', border: 'border-warning/20' },
  alert: { badge: 'bg-danger/10 text-danger', icon: 'bg-danger/10 text-danger', border: 'border-danger/20' },
  neutral: { badge: 'bg-muted text-muted-foreground', icon: 'bg-muted text-muted-foreground', border: 'border-border' },
}

export function formatMetricValue(reading: SensorReading, metric: MetricDefinition): string {
  const value = reading[metric.key]
  return formatValue(value, metric)
}

export function metricStatus(reading: SensorReading, metric: MetricDefinition): { label: string; tone: StatusTone } {
  const value = reading[metric.key]
  if (value === null) return { label: 'Not available', tone: 'neutral' }
  if (metric.key === 'aqi') {
    if (value <= 1) return { label: 'Excellent', tone: 'healthy' }
    if (value <= 2) return { label: 'Good', tone: 'healthy' }
    if (value <= 3) return { label: 'Moderate', tone: 'warning' }
    return { label: 'Poor', tone: 'alert' }
  }
  if (metric.key === 'tvoc') return value > 100 ? { label: 'Elevated', tone: 'alert' } : { label: 'Normal', tone: 'healthy' }
  return { label: 'Stored reading', tone: 'neutral' }
}

export function overallStatus(reading: SensorReading): { label: string; detail: string; tone: StatusTone } {
  if (reading.tvoc === null || reading.aqi === null) {
    return { label: 'Air quality unavailable', detail: 'Required air-quality measurements are missing. Check the sensor connection; unavailable values are not healthy readings.', tone: 'neutral' }
  }
  if ((reading.tvoc !== null && reading.tvoc > 100) || (reading.aqi !== null && reading.aqi >= 4)) {
    return { label: 'Attention needed', detail: 'An air-quality reading is above the current dashboard reference.', tone: 'alert' }
  }
  if (reading.aqi === 3) {
    return { label: 'Moderate air quality', detail: 'Conditions are usable, but continued monitoring is recommended.', tone: 'warning' }
  }
  return { label: 'Air quality looks healthy', detail: 'Current readings are within the normal dashboard reference range.', tone: 'healthy' }
}
