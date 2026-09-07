<script setup lang="ts">
import { AlertTriangle, Bell, BellOff, CheckCircle2, Loader2, Volume2 } from '@lucide/vue'
import { ref } from 'vue'
import { actuatorsApi } from '../../services/api'
import type { ActuatorAlertResponse } from '../../types/settings'

const props = defineProps<{
  manualOverride: boolean
  manualAlertEnabled: boolean
}>()

const emit = defineEmits<{
  (e: 'updated', response: ActuatorAlertResponse): void
}>()

const loading = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref<'success' | 'error'>('success')

async function handleSetAlert(enabled: boolean): Promise<void> {
  loading.value = true
  feedbackMessage.value = ''
  try {
    const response = await actuatorsApi.setAlert(enabled)
    feedbackType.value = 'success'
    feedbackMessage.value = response.message
    emit('updated', response)
  } catch (err) {
    feedbackType.value = 'error'
    feedbackMessage.value = err instanceof Error ? err.message : 'Actuator command failed.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="panel p-6">
    <div class="flex items-start justify-between gap-4">
      <div>
        <p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">Hardware Actuator</p>
        <h3 class="mt-1 text-xl font-bold text-foreground">Actuator Test</h3>
        <p class="mt-1.5 text-sm text-muted-foreground">
          Manually trigger or stop the Arduino red LED and buzzer alarm.
        </p>
      </div>
      <span class="grid h-11 w-11 place-items-center rounded-2xl bg-surface-blue text-primary">
        <Volume2 :size="20" />
      </span>
    </div>

    <!-- Active State Card -->
    <div
      class="mt-5 rounded-2xl border p-4 transition-colors"
      :class="props.manualOverride && props.manualAlertEnabled
        ? 'border-danger/30 bg-danger/10 text-danger'
        : 'border-border bg-muted/40 text-muted-foreground'"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <span
            class="inline-block h-2.5 w-2.5 rounded-full"
            :class="props.manualOverride && props.manualAlertEnabled
              ? 'bg-danger animate-ping'
              : 'bg-muted-foreground/60'"
          />
          <span class="text-sm font-bold text-foreground">
            {{ props.manualOverride && props.manualAlertEnabled ? 'Manual Alert Active' : 'Automatic Monitoring' }}
          </span>
        </div>
        <span class="text-xs font-semibold">
          Mode: <strong class="font-bold text-foreground">{{ props.manualOverride ? 'Manual Override' : 'Automatic' }}</strong>
        </span>
      </div>
      <p class="mt-2 text-xs leading-relaxed opacity-90">
        {{ props.manualOverride && props.manualAlertEnabled
          ? 'Manual alert is currently overriding automatic sensor evaluation. Stop the alert to resume normal threshold checking.'
          : 'Actuator state is automatically controlled by edge analytics based on current TVOC readings.' }}
      </p>
    </div>

    <!-- Action Buttons -->
    <div class="mt-6 flex flex-wrap items-center gap-3">
      <button
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-xl bg-danger px-4 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-danger/90 disabled:opacity-50"
        :disabled="loading || (props.manualOverride && props.manualAlertEnabled)"
        @click="handleSetAlert(true)"
      >
        <Loader2 v-if="loading" :size="16" class="animate-spin" />
        <Bell v-else :size="16" />
        <span>Test Alert</span>
      </button>

      <button
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-bold text-foreground shadow-sm transition hover:bg-muted disabled:opacity-50"
        :disabled="loading || (!props.manualOverride && !props.manualAlertEnabled)"
        @click="handleSetAlert(false)"
      >
        <Loader2 v-if="loading" :size="16" class="animate-spin" />
        <BellOff v-else :size="16" />
        <span>Stop Alert</span>
      </button>
    </div>

    <!-- Feedback Message Banner -->
    <div
      v-if="feedbackMessage"
      class="mt-4 flex items-center gap-2 rounded-xl border p-3 text-xs font-medium"
      :class="feedbackType === 'success'
        ? 'border-success/20 bg-success/10 text-success'
        : 'border-danger/20 bg-danger/10 text-danger'"
    >
      <CheckCircle2 v-if="feedbackType === 'success'" :size="16" class="shrink-0" />
      <AlertTriangle v-else :size="16" class="shrink-0" />
      <span>{{ feedbackMessage }}</span>
    </div>
  </section>
</template>
