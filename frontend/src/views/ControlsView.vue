<script setup lang="ts">
import { AlertCircle, RefreshCw } from '@lucide/vue'
import { onMounted, ref } from 'vue'
import ActuatorControl from '../components/controls/ActuatorControl.vue'
import DeviceStatusCard from '../components/controls/DeviceStatusCard.vue'
import ThresholdControl from '../components/controls/ThresholdControl.vue'
import { deviceApi, readingsApi, settingsApi } from '../services/api'
import type { SensorReading } from '../types/reading'
import type { ActuatorAlertResponse, DeviceStatus, SystemSettings } from '../types/settings'

const reading = ref<SensorReading | null>(null)
const settings = ref<SystemSettings | null>(null)
const deviceStatus = ref<DeviceStatus | null>(null)

const loading = ref(true)
const statusLoading = ref(false)
const error = ref('')

async function loadData(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    const [latestReading, currentSettings, status] = await Promise.all([
      readingsApi.getLatest().catch(() => null),
      settingsApi.getSettings(),
      deviceApi.getStatus().catch(() => null),
    ])
    reading.value = latestReading
    settings.value = currentSettings
    deviceStatus.value = status
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load control settings.'
  } finally {
    loading.value = false
  }
}

async function refreshDeviceStatus(): Promise<void> {
  statusLoading.value = true
  try {
    const status = await deviceApi.getStatus()
    deviceStatus.value = status
  } catch {
    // Keep existing status if refresh fails
  } finally {
    statusLoading.value = false
  }
}

function handleThresholdUpdated(newThreshold: number): void {
  if (settings.value) {
    settings.value.tvoc_threshold = newThreshold
  }
}

function handleActuatorUpdated(response: ActuatorAlertResponse): void {
  if (settings.value) {
    settings.value.manual_override = response.manual_override
    settings.value.manual_alert_enabled = response.requested_alert
  }
}

onMounted(loadData)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm font-semibold text-primary">System Management</p>
        <h2 class="mt-1 text-2xl font-bold tracking-[-0.03em] text-foreground sm:text-3xl">
          Controls & Configuration
        </h2>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
          Manage the TVOC alert threshold rule, trigger manual actuator tests, and inspect edge node health.
        </p>
      </div>
      <button
        class="flex items-center gap-2 rounded-xl border border-border bg-card px-3.5 py-2.5 text-sm font-semibold text-muted-foreground shadow-sm hover:border-primary/30 hover:text-primary"
        :disabled="loading"
        @click="loadData"
      >
        <RefreshCw :size="16" :class="loading ? 'animate-spin' : ''" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Error State -->
    <div
      v-if="error"
      class="flex flex-col items-start justify-between gap-4 rounded-app border border-danger/25 bg-danger/10 p-5 sm:flex-row sm:items-center"
    >
      <div class="flex items-center gap-3">
        <AlertCircle :size="20" class="text-danger shrink-0" />
        <div>
          <p class="font-bold text-danger">Controls Unavailable</p>
          <p class="mt-0.5 text-sm text-danger">{{ error }}</p>
        </div>
      </div>
      <button
        class="rounded-xl bg-card px-4 py-2 text-sm font-bold text-danger shadow-sm hover:bg-muted"
        @click="loadData"
      >
        Try again
      </button>
    </div>

    <!-- Main Content -->
    <template v-else-if="settings">
      <div class="grid gap-6 lg:grid-cols-2">
        <!-- 1. Threshold Configuration -->
        <ThresholdControl
          :threshold="settings.tvoc_threshold"
          :current-tvoc="reading?.tvoc ?? null"
          @updated="handleThresholdUpdated"
        />

        <!-- 2. Actuator Manual Test -->
        <ActuatorControl
          :manual-override="settings.manual_override"
          :manual-alert-enabled="settings.manual_alert_enabled"
          @updated="handleActuatorUpdated"
        />
      </div>

      <!-- 3. Device & Edge Diagnostic Status -->
      <DeviceStatusCard
        :status="deviceStatus"
        :loading="statusLoading"
        @refresh="refreshDeviceStatus"
      />
    </template>

    <!-- Skeleton Loading -->
    <div v-else class="grid gap-6 lg:grid-cols-2">
      <div class="panel h-80 animate-pulse bg-muted" />
      <div class="panel h-80 animate-pulse bg-muted" />
    </div>
  </div>
</template>
