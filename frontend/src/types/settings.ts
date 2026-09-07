export interface SystemSettings {
  tvoc_threshold: number
  manual_override: boolean
  manual_alert_enabled: boolean
}

export interface TvocThresholdUpdate {
  value: number
}

export interface ActuatorAlertRequest {
  enabled: boolean
}

export interface ActuatorAlertResponse {
  accepted: boolean
  manual_override: boolean
  requested_alert: boolean
  message: string
}

export interface DeviceStatus {
  edge_api: string
  arduino_connected: boolean
  serial_port: string | null
  baud_rate: number
  last_reading_at: string | null
}
