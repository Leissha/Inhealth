<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MetricChart from '../components/analytics/MetricChart.vue'
import ReadingsTable from '../components/analytics/ReadingsTable.vue'
import StatCard from '../components/analytics/StatCard.vue'
import { readingsApi } from '../services/api'
import type { MetricName, ReadingHistoryResponse, ReadingStatsResponse } from '../types/reading'
import { analyticsMetrics, isMetricName, metricDefinitions } from '../utils/metrics'

const route = useRoute()
const router = useRouter()
const initialMetric = isMetricName(route.query.metric) ? route.query.metric : 'tvoc'
const selectedMetric = ref<MetricName>(initialMetric)
const selectedRange = ref(24)
const history = ref<ReadingHistoryResponse | null>(null)
const stats = ref<ReadingStatsResponse | null>(null)
const loading = ref(false)
const error = ref('')
const ranges = [1, 6, 12, 24]
const metric = computed(() => metricDefinitions[selectedMetric.value])

function statValue(value: number | null): string {
  if (value === null) return '—'
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: metric.value.decimals ?? 1,
  })
}

async function loadAnalytics(): Promise<void> {
  loading.value = true
  error.value = ''
  history.value = null
  stats.value = null
  try {
    const [historyResponse, statsResponse] = await Promise.all([
      readingsApi.getHistory(selectedMetric.value, selectedRange.value, 200),
      readingsApi.getStats(selectedMetric.value, selectedRange.value),
    ])
    history.value = historyResponse
    stats.value = statsResponse
  } catch (caughtError) {
    error.value = caughtError instanceof Error ? caughtError.message : 'Analytics could not be loaded.'
  } finally {
    loading.value = false
  }
}

watch(selectedMetric, (value) => {
  router.replace({ query: { ...route.query, metric: value } })
})
watch([selectedMetric, selectedRange], loadAnalytics, { immediate: true })
</script>

<template>
  <div>
    <div><p class="text-sm font-semibold text-primary">Database-backed insights</p><h2 class="mt-1 text-2xl font-bold tracking-[-0.03em] text-foreground sm:text-3xl">Explore sensor history</h2><p class="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">Compare valid readings over time and review minimum, average, and maximum values calculated by MariaDB.</p></div>

    <section class="panel mt-7 grid gap-5 p-5 sm:grid-cols-2 sm:p-6">
      <label class="block"><span class="mb-2 block text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground">Metric</span><select v-model="selectedMetric" class="w-full rounded-xl border border-border bg-card px-3.5 py-2.5 text-sm font-semibold text-foreground outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"><option v-for="option in analyticsMetrics" :key="option.key" :value="option.key">{{ option.label }}</option></select></label>
      <fieldset><legend class="mb-2 text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground">Time range</legend><div class="grid grid-cols-4 gap-2"><button v-for="range in ranges" :key="range" type="button" class="rounded-xl border px-3 py-2.5 text-sm font-bold transition" :class="selectedRange === range ? 'border-primary bg-primary text-primary-foreground' : 'border-border bg-card text-muted-foreground hover:border-primary/30 hover:text-primary'" @click="selectedRange = range">{{ range }}h</button></div></fieldset>
    </section>

    <div v-if="error" class="mt-6 flex items-center justify-between gap-4 rounded-app border border-danger/25 bg-danger/10 p-5"><div><p class="font-bold text-danger">Analytics unavailable</p><p class="mt-1 text-sm text-danger">{{ error }}</p></div><button class="rounded-xl bg-card px-4 py-2 text-sm font-bold text-danger shadow-sm" @click="loadAnalytics">Try again</button></div>

    <template v-else>
      <div class="mt-6 grid gap-4 sm:grid-cols-3">
        <StatCard label="Minimum" :value="statValue(stats?.minimum ?? null)" :unit="metric.unit" :available="stats?.minimum != null" />
        <StatCard label="Average" :value="statValue(stats?.average ?? null)" :unit="metric.unit" :available="stats?.average != null" />
        <StatCard label="Maximum" :value="statValue(stats?.maximum ?? null)" :unit="metric.unit" :available="stats?.maximum != null" />
      </div>
      <p v-if="stats" class="mt-3 text-right text-xs font-medium text-muted-foreground">{{ stats.count }} valid {{ stats.count === 1 ? 'sample' : 'samples' }}</p>
      <div class="mt-6"><MetricChart :points="history?.points ?? []" :metric="metric" :loading="loading" :range-hours="selectedRange" /></div>
      <div class="mt-6"><ReadingsTable :points="history?.points ?? []" :metric="metric" /></div>
    </template>
  </div>
</template>
