<script setup lang="ts">
import { ArrowUpRight } from '@lucide/vue'
import { RouterLink } from 'vue-router'
import { statusToneClasses, type MetricDefinition, type StatusTone } from '../../utils/metrics'

const props = defineProps<{ metric: MetricDefinition; value: string; status: string; tone: StatusTone }>()
</script>

<template>
  <RouterLink :to="`/analytics?metric=${metric.key}`" class="panel group relative overflow-hidden p-5 transition hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-md">
    <div class="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-surface-soft/70 to-transparent" />
    <div class="relative flex items-start justify-between gap-4">
      <span class="grid h-10 w-10 place-items-center rounded-2xl bg-surface-blue text-primary"><component :is="metric.icon" :size="20" :stroke-width="2" /></span>
      <ArrowUpRight :size="17" class="text-muted-foreground/40 transition group-hover:text-primary" />
    </div>
    <div class="relative mt-5 flex items-end gap-1.5"><span class="text-3xl font-bold tracking-[-0.04em] text-foreground">{{ value }}</span><span v-if="value !== '—' && metric.unit" class="pb-1 text-sm font-semibold text-muted-foreground/70">{{ metric.unit }}</span></div>
    <div class="relative mt-2 flex items-center justify-between gap-2"><p class="truncate text-sm font-semibold text-muted-foreground">{{ metric.label }}</p><span class="whitespace-nowrap rounded-full px-2 py-1 text-[10px] font-bold" :class="statusToneClasses[tone].badge">{{ status }}</span></div>
  </RouterLink>
</template>
