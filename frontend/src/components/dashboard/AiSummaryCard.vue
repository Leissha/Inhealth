<script setup lang="ts">
import { ref } from 'vue'
import { Sparkles } from '@lucide/vue'
import { summaryApi } from '../../services/api'
import type { SummaryResponse } from '../../types/summary'

const RANGE_HOURS = 1
const summary = ref<SummaryResponse | null>(null)
const loading = ref(false)
const error = ref('')

async function generateSummary(): Promise<void> {
  loading.value = true
  error.value = ''
  try {
    summary.value = await summaryApi.generate(RANGE_HOURS)
  } catch (caughtError) {
    summary.value = null
    error.value = caughtError instanceof Error
      ? caughtError.message
      : 'The current overview could not be generated.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="panel p-5 sm:p-6">
    <div class="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
      <div class="flex gap-3">
        <span class="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-surface-blue text-primary"><Sparkles :size="19" /></span>
        <div>
          <p class="text-xs font-bold uppercase tracking-[0.13em] text-primary">Current overview</p>
          <h2 class="mt-1 text-xl font-bold text-foreground">AI Summary</h2>
          <p class="mt-1 max-w-3xl text-sm leading-6 text-muted-foreground">Explain the last hour of indoor readings, alert activity and Hawthorn outdoor PM context.</p>
        </div>
      </div>
      <button type="button" class="shrink-0 rounded-xl bg-primary px-4 py-2.5 text-sm font-bold text-primary-foreground disabled:cursor-not-allowed disabled:opacity-60" :disabled="loading" @click="generateSummary">{{ loading ? 'Generating…' : summary ? 'Refresh AI Summary' : 'Generate AI Summary' }}</button>
    </div>

    <div v-if="summary" class="mt-5 rounded-xl border border-border bg-muted/40 p-4">
      <p class="text-xs font-bold uppercase tracking-wider text-muted-foreground">Last hour · {{ summary.sample_count }} local samples</p>
      <p class="mt-2 text-sm leading-6 text-foreground">{{ summary.summary }}</p>
      <p v-if="summary.outdoor.available" class="mt-3 text-xs text-muted-foreground">Outdoor context: Open-Meteo / CAMS modelled data, Hawthorn</p>
    </div>
    <p v-else-if="error" class="mt-4 rounded-xl border border-danger/25 bg-danger/10 p-4 text-sm text-danger">{{ error }}</p>
    <p class="mt-3 text-xs leading-5 text-muted-foreground">Indicative prototype readings only. Inhealth is not a certified safety or medical device.</p>
  </section>
</template>
