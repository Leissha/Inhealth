<script setup lang="ts">
import { CategoryScale, Chart, Filler, Legend, LineController, LineElement, LinearScale, PointElement, Tooltip, type ChartConfiguration } from 'chart.js'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { HistoryPoint } from '../../types/reading'
import { getChartTheme } from '../../utils/chartTheme'

Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Legend, Filler)
const props = defineProps<{ points: HistoryPoint[]; loading?: boolean }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null
const hasData = computed(() => props.points.length > 0)
const formatLabel = (timestamp: string) => new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit' }).format(new Date(timestamp))

function renderChart(): void {
  chart?.destroy(); chart = null
  if (!canvas.value || !hasData.value) return
  const theme = getChartTheme()
  const configuration: ChartConfiguration<'line'> = {
    type: 'line',
    data: {
      labels: props.points.map((point) => formatLabel(point.recorded_at)),
      datasets: [{ label: 'TVOC (ppb)', data: props.points.map((point) => point.value), borderColor: theme.primary, backgroundColor: theme.primarySoft, borderWidth: 2, pointRadius: props.points.length > 48 ? 0 : 2, pointHoverRadius: 4, pointBackgroundColor: theme.primary, tension: 0.32, fill: true }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: false, interaction: { intersect: false, mode: 'index' },
      plugins: { legend: { display: false }, tooltip: { backgroundColor: theme.foreground, padding: 11, displayColors: false, callbacks: { label: (context) => `${context.parsed.y} ppb` } } },
      scales: {
        x: { grid: { display: false }, ticks: { color: theme.mutedForeground, maxTicksLimit: 7, maxRotation: 0 }, border: { display: false } },
        y: { beginAtZero: false, grid: { color: theme.grid }, ticks: { color: theme.mutedForeground, padding: 8 }, border: { display: false } },
      },
    },
  }
  chart = new Chart(canvas.value, configuration)
}
watch(() => props.points, () => nextTick(renderChart), { deep: true, immediate: true })
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <section class="panel p-5 sm:p-6">
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div><p class="text-xs font-bold uppercase tracking-[0.13em] text-primary">Recent trend</p><h2 class="mt-1 text-xl font-bold tracking-tight text-foreground">TVOC over 24 hours</h2><p class="mt-1 text-sm text-muted-foreground">Volatile organic compounds measured at the edge.</p></div>
      <span class="rounded-full bg-surface-blue px-3 py-1.5 text-xs font-bold text-primary">Last 24 hours</span>
    </div>
    <div class="mt-6 h-[280px] sm:h-[320px]">
      <div v-if="loading" class="h-full animate-pulse rounded-2xl bg-muted" />
      <div v-else-if="!hasData" class="grid h-full place-items-center rounded-2xl border border-dashed border-border bg-muted/50 text-sm text-muted-foreground">No TVOC history is available for this period.</div>
      <canvas v-else ref="canvas" aria-label="TVOC readings over the last 24 hours" />
    </div>
  </section>
</template>
