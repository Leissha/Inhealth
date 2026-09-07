<script setup lang="ts">
import { ArrowRight, RefreshCw, SlidersHorizontal } from '@lucide/vue'
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import MetricCard from '../components/dashboard/MetricCard.vue'
import StatusCard from '../components/dashboard/StatusCard.vue'
import TrendChart from '../components/dashboard/TrendChart.vue'
import AiSummaryCard from '../components/dashboard/AiSummaryCard.vue'
import { readingsApi } from '../services/api'
import type { ReadingHistoryResponse, SensorReading } from '../types/reading'
import { formatMetricValue, metricStatus, overallStatus, primaryMetrics, secondaryMetrics } from '../utils/metrics'

const reading = ref<SensorReading | null>(null)
const history = ref<ReadingHistoryResponse | null>(null)
const loading = ref(true)
const error = ref('')
const status = computed(() => reading.value ? overallStatus(reading.value) : null)
const updatedAt = computed(() => reading.value
  ? new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(reading.value.recorded_at))
  : 'unknown')

async function loadDashboard(): Promise<void> {
  loading.value = true; error.value = ''
  try {
    const [latestReading, tvocHistory] = await Promise.all([readingsApi.getLatest(), readingsApi.getHistory('tvoc', 24, 200)])
    reading.value = latestReading; history.value = tvocHistory
  } catch (caughtError) {
    error.value = caughtError instanceof Error ? caughtError.message : 'The dashboard could not be loaded.'
  } finally { loading.value = false }
}
onMounted(loadDashboard)
</script>

<template>
  <div>
    <div class="flex flex-wrap items-end justify-between gap-4">
      <div><p class="text-sm font-semibold text-primary">Live room overview</p><h2 class="mt-1 text-2xl font-bold tracking-[-0.03em] text-foreground sm:text-3xl">Indoor air, at a glance</h2><p class="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">Current sensor readings and the latest air-quality trend from the edge database.</p></div>
      <button class="flex items-center gap-2 rounded-xl border border-border bg-card px-3.5 py-2.5 text-sm font-semibold text-muted-foreground shadow-sm hover:border-primary/30 hover:text-primary" :disabled="loading" @click="loadDashboard"><RefreshCw :size="16" :class="loading ? 'animate-spin' : ''" />Refresh</button>
    </div>

    <div class="mt-6"><AiSummaryCard /></div>

    <div v-if="error" class="mt-6 flex flex-col items-start justify-between gap-4 rounded-app border border-danger/25 bg-danger/10 p-5 sm:flex-row sm:items-center">
      <div><p class="font-bold text-danger">Dashboard unavailable</p><p class="mt-1 text-sm text-danger">{{ error }}</p></div>
      <button class="rounded-xl bg-card px-4 py-2 text-sm font-bold text-danger shadow-sm" @click="loadDashboard">Try again</button>
    </div>

    <template v-else-if="reading">
      <div class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <MetricCard v-for="metric in primaryMetrics" :key="metric.key" :metric="metric" :value="formatMetricValue(reading, metric)" :status="metricStatus(reading, metric).label" :tone="metricStatus(reading, metric).tone" />
      </div>
      <div class="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1.75fr)_minmax(300px,0.75fr)]">
        <TrendChart :points="history?.points ?? []" :loading="loading" />
        <div class="space-y-6">
          <StatusCard v-if="status" :label="status.label" :detail="status.detail" :tone="status.tone" :updated-at="updatedAt" />
          <section class="panel p-5">
            <div class="flex items-start justify-between gap-4"><div><p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Alert reference</p><h2 class="mt-1 text-lg font-bold text-foreground">TVOC threshold</h2></div><span class="grid h-10 w-10 place-items-center rounded-2xl bg-surface-blue text-primary"><SlidersHorizontal :size="19" /></span></div>
            <p class="mt-4 text-sm leading-6 text-muted-foreground">Adjust the active TVOC alert threshold or trigger actuator tests.</p>
            <RouterLink to="/controls" class="mt-4 inline-flex items-center gap-2 text-sm font-bold text-primary hover:text-primary/80">Configure in controls <ArrowRight :size="16" /></RouterLink>
          </section>
        </div>
      </div>
      <section class="mt-6 panel p-5 sm:p-6">
        <div><p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Additional sensors</p><h2 class="mt-1 text-lg font-bold text-foreground">Detailed readings</h2></div>
        <div class="mt-5 grid gap-3 sm:grid-cols-3">
          <div v-for="metric in secondaryMetrics" :key="metric.key" class="rounded-2xl border border-border bg-muted/50 p-4">
            <div class="flex items-center gap-2 text-muted-foreground"><component :is="metric.icon" :size="16" /><span class="text-xs font-bold uppercase tracking-wide">{{ metric.label }}</span></div>
            <p class="mt-3 text-xl font-bold text-foreground">{{ formatMetricValue(reading, metric) }} <span v-if="reading[metric.key] !== null" class="text-xs font-semibold text-muted-foreground/70">{{ metric.unit }}</span></p>
            <p v-if="reading[metric.key] === null" class="mt-1 text-xs text-muted-foreground/70">Not available</p>
          </div>
        </div>
      </section>
    </template>
    <div v-else class="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-3"><div v-for="index in 6" :key="index" class="panel h-44 animate-pulse bg-muted" /></div>
  </div>
</template>
