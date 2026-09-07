<script setup lang="ts">
import { Activity, Cpu, HardDrive, RefreshCw, Radio } from '@lucide/vue'
import { computed } from 'vue'
import type { DeviceStatus } from '../../types/settings'

const props = defineProps<{
  status: DeviceStatus | null
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const formattedLastReading = computed(() => {
  if (!props.status?.last_reading_at) return 'No readings yet'
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'medium',
    }).format(new Date(props.status.last_reading_at))
  } catch {
    return props.status.last_reading_at
  }
})
</script>

<template>
  <section class="panel p-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Edge Infrastructure</p>
        <h3 class="mt-1 text-xl font-bold text-foreground">Device & Edge Status</h3>
        <p class="mt-1.5 text-sm text-muted-foreground">
          Real-time health of the edge API, serial connection, and sensor ingestion.
        </p>
      </div>
      <button
        class="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold text-muted-foreground shadow-sm transition hover:border-primary/30 hover:text-primary"
        :disabled="props.loading"
        @click="emit('refresh')"
      >
        <RefreshCw :size="14" :class="props.loading ? 'animate-spin' : ''" />
        <span>Refresh</span>
      </button>
    </div>

    <!-- Diagnostic Grid -->
    <div class="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Edge API -->
      <div class="rounded-2xl border border-border bg-muted/30 p-4">
        <div class="flex items-center gap-2 text-muted-foreground">
          <Activity :size="16" />
          <span class="text-xs font-bold uppercase tracking-wider">Edge API</span>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <span class="inline-block h-2.5 w-2.5 rounded-full bg-success" />
          <p class="text-lg font-bold text-foreground capitalize">{{ props.status?.edge_api ?? 'Online' }}</p>
        </div>
        <p class="mt-1 text-xs text-muted-foreground">FastAPI service active</p>
      </div>

      <!-- Arduino Connection -->
      <div class="rounded-2xl border border-border bg-muted/30 p-4">
        <div class="flex items-center gap-2 text-muted-foreground">
          <Cpu :size="16" />
          <span class="text-xs font-bold uppercase tracking-wider">Arduino Node</span>
        </div>
        <div class="mt-3 flex items-center gap-2">
          <span
            class="inline-block h-2.5 w-2.5 rounded-full"
            :class="props.status?.arduino_connected ? 'bg-success' : 'bg-warning'"
          />
          <p class="text-lg font-bold text-foreground">
            {{ props.status?.arduino_connected ? 'Connected' : 'Stale / Idle' }}
          </p>
        </div>
        <p class="mt-1 text-xs text-muted-foreground">
          {{ props.status?.arduino_connected ? 'Receiving live samples' : 'No recent samples received' }}
        </p>
      </div>

      <!-- Serial Interface -->
      <div class="rounded-2xl border border-border bg-muted/30 p-4">
        <div class="flex items-center gap-2 text-muted-foreground">
          <Radio :size="16" />
          <span class="text-xs font-bold uppercase tracking-wider">Serial Port</span>
        </div>
        <p class="mt-3 text-lg font-bold text-foreground truncate">
          {{ props.status?.serial_port || 'Auto-detect' }}
        </p>
        <p class="mt-1 text-xs text-muted-foreground">
          Baud Rate: {{ props.status?.baud_rate ?? 9600 }}
        </p>
      </div>

      <!-- Last Reading Timestamp -->
      <div class="rounded-2xl border border-border bg-muted/30 p-4">
        <div class="flex items-center gap-2 text-muted-foreground">
          <HardDrive :size="16" />
          <span class="text-xs font-bold uppercase tracking-wider">Last Reading</span>
        </div>
        <p class="mt-3 text-sm font-bold text-foreground truncate">
          {{ formattedLastReading }}
        </p>
        <p class="mt-1 text-xs text-muted-foreground">Ingested into MariaDB</p>
      </div>
    </div>
  </section>
</template>
