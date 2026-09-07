<script setup lang="ts">
defineProps<{ label: string; value: string; unit: string; available: boolean }>()
</script>
<template>
  <div class="panel p-5">
    <p class="text-xs font-bold uppercase tracking-[0.13em] text-muted-foreground/70">{{ label }}</p>
    <p class="mt-3 text-2xl font-bold tracking-tight text-foreground">{{ value }} <span v-if="available && unit" class="text-sm font-semibold text-muted-foreground">{{ unit }}</span></p>
    <p v-if="!available" class="mt-1 text-xs text-muted-foreground">Not available</p>
  </div>
</template>

