<script setup lang="ts">
import { AlertCircle, CheckCircle2, Loader2, Save, SlidersHorizontal } from '@lucide/vue'
import { computed, ref, watch } from 'vue'
import { settingsApi } from '../../services/api'

const props = defineProps<{
  threshold: number
  currentTvoc: number | null
}>()

const emit = defineEmits<{
  (e: 'updated', newThreshold: number): void
}>()

const inputValue = ref<number>(props.threshold)
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

watch(
  () => props.threshold,
  (newVal) => {
    inputValue.value = newVal
  },
)

const isUnchanged = computed(() => inputValue.value === props.threshold)

const statusInfo = computed(() => {
  if (props.currentTvoc === null) {
    return {
      label: 'Unavailable',
      detail: 'Current TVOC sensor reading is not available.',
      tone: 'neutral',
      badgeClass: 'bg-muted text-muted-foreground border-border',
    }
  }
  if (props.currentTvoc > props.threshold) {
    return {
      label: 'Above threshold',
      detail: `Current TVOC (${props.currentTvoc} ppb) exceeds the active rule limit (${props.threshold} ppb).`,
      tone: 'alert',
      badgeClass: 'bg-danger/10 text-danger border-danger/20',
    }
  }
  return {
    label: 'Normal',
    detail: `Current TVOC (${props.currentTvoc} ppb) is within the safe limit (${props.threshold} ppb).`,
    tone: 'healthy',
    badgeClass: 'bg-success/10 text-success border-success/20',
  }
})

async function handleSave(): Promise<void> {
  successMessage.value = ''
  errorMessage.value = ''

  const value = Number(inputValue.value)
  if (isNaN(value) || value < 0) {
    errorMessage.value = 'Threshold must be a valid positive number.'
    return
  }

  saving.value = true
  try {
    const updated = await settingsApi.updateTvocThreshold(value)
    inputValue.value = updated.tvoc_threshold
    emit('updated', updated.tvoc_threshold)
    successMessage.value = `TVOC threshold successfully updated to ${updated.tvoc_threshold} ppb.`
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : 'Failed to update TVOC threshold.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="panel p-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Edge Rule Engine</p>
        <h3 class="mt-1 text-xl font-bold text-foreground">Alert Configuration</h3>
        <p class="mt-1.5 text-sm text-muted-foreground">
          Configure the conditional TVOC rule stored in the edge database.
        </p>
      </div>
      <span class="grid h-11 w-11 place-items-center rounded-2xl bg-surface-blue text-primary">
        <SlidersHorizontal :size="20" />
      </span>
    </div>

    <!-- Live Status Banner -->
    <div class="mt-5 rounded-2xl border p-4" :class="statusInfo.badgeClass">
      <div class="flex items-center justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <span class="inline-block h-2.5 w-2.5 rounded-full" :class="statusInfo.tone === 'alert' ? 'bg-danger animate-ping' : statusInfo.tone === 'healthy' ? 'bg-success' : 'bg-muted-foreground'" />
          <span class="text-sm font-bold">{{ statusInfo.label }}</span>
        </div>
        <span class="text-xs font-semibold">
          Live TVOC: <strong class="font-bold">{{ props.currentTvoc !== null ? `${props.currentTvoc} ppb` : '—' }}</strong>
        </span>
      </div>
      <p class="mt-1.5 text-xs opacity-90 leading-relaxed">{{ statusInfo.detail }}</p>
    </div>

    <!-- Input Form -->
    <form class="mt-6 space-y-4" @submit.prevent="handleSave">
      <div>
        <label for="tvoc-threshold-input" class="block text-xs font-bold uppercase tracking-wider text-muted-foreground">
          TVOC Threshold (ppb)
        </label>
        <div class="relative mt-2 flex items-center">
          <input id="tvoc-threshold-input" v-model.number="inputValue" type="number" min="0" max="10000" step="1"
            class="w-full rounded-xl border border-border bg-card px-4 py-2.5 pr-14 text-base font-semibold text-foreground shadow-sm transition focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
            :disabled="saving"
          />
          <span class="pointer-events-none absolute right-4 text-xs font-bold text-muted-foreground">ppb</span>
        </div>
      </div>

      <!-- Feedback Messages -->
      <div v-if="successMessage" class="flex items-center gap-2 rounded-xl border border-success/20 bg-success/10 p-3 text-xs font-medium text-success">
        <CheckCircle2 :size="16" class="shrink-0" />
        <span>{{ successMessage }}</span>
      </div>

      <div v-if="errorMessage" class="flex items-center gap-2 rounded-xl border border-danger/20 bg-danger/10 p-3 text-xs font-medium text-danger">
        <AlertCircle :size="16" class="shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>

      <div class="flex items-center justify-end gap-3 pt-2">
        <button
          type="submit"
          class="flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-bold text-primary-foreground shadow-sm transition hover:bg-primary/90 disabled:opacity-50"
          :disabled="saving || isUnchanged"
        >
          <Loader2 v-if="saving" :size="16" class="animate-spin" />
          <Save v-else :size="16" />
          <span>{{ saving ? 'Saving...' : 'Save threshold' }}</span>
        </button>
      </div>
    </form>
  </section>
</template>
