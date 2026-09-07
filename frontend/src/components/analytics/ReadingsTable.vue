<script setup lang="ts">
import type { HistoryPoint } from '../../types/reading'
import { formatValue, type MetricDefinition } from '../../utils/metrics'

defineProps<{ points: HistoryPoint[]; metric: MetricDefinition }>()
const formatTimestamp = (timestamp: string) => new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(timestamp))
</script>
<template>
  <section class="panel overflow-hidden">
    <div class="border-b border-border px-5 py-4 sm:px-6"><p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Recent samples</p><h2 class="mt-1 text-lg font-bold text-foreground">Latest valid readings</h2></div>
    <div v-if="points.length" class="overflow-x-auto">
      <table class="w-full text-left text-sm">
        <thead class="bg-muted/60 text-xs uppercase tracking-wide text-muted-foreground"><tr><th class="px-5 py-3 font-bold sm:px-6">Timestamp</th><th class="px-5 py-3 text-right font-bold sm:px-6">{{ metric.label }}</th></tr></thead>
        <tbody class="divide-y divide-border"><tr v-for="point in points.slice(-10).reverse()" :key="point.recorded_at" class="hover:bg-muted/30"><td class="whitespace-nowrap px-5 py-3.5 text-muted-foreground sm:px-6">{{ formatTimestamp(point.recorded_at) }}</td><td class="whitespace-nowrap px-5 py-3.5 text-right font-bold text-foreground sm:px-6">{{ formatValue(point.value, metric) }} <span v-if="metric.unit" class="font-medium text-muted-foreground">{{ metric.unit }}</span></td></tr></tbody>
      </table>
    </div>
    <p v-else class="px-6 py-10 text-center text-sm text-muted-foreground">No valid readings are available for this period.</p>
  </section>
</template>

