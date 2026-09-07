<script setup lang="ts">
import { AlertTriangle, CheckCircle2, Clock3 } from '@lucide/vue'
import { computed } from 'vue'
import { statusToneClasses, type StatusTone } from '../../utils/metrics'

const props = defineProps<{ label: string; detail: string; tone: StatusTone; updatedAt: string }>()
const presentation = computed(() => {
  const iconComponent = props.tone === 'healthy' ? CheckCircle2 : AlertTriangle
  return { iconComponent, ...statusToneClasses[props.tone] }
})
</script>

<template>
  <section class="panel p-5" :class="presentation.border">
    <div class="flex items-start gap-4">
      <span class="grid h-11 w-11 shrink-0 place-items-center rounded-2xl" :class="presentation.icon"><component :is="presentation.iconComponent" :size="22" /></span>
      <div class="min-w-0"><p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Current status</p><h2 class="mt-1 text-lg font-bold tracking-tight text-foreground">{{ label }}</h2><p class="mt-1 text-sm leading-5 text-muted-foreground">{{ detail }}</p></div>
    </div>
    <div class="mt-5 flex items-center gap-2 border-t border-border pt-4 text-xs font-medium text-muted-foreground"><Clock3 :size="15" />Last reading {{ updatedAt }}</div>
  </section>
</template>
