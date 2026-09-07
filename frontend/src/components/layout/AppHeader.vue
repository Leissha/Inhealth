<script setup lang="ts">
import { Menu } from '@lucide/vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

defineEmits<{ openMenu: [] }>()
const route = useRoute()
const title = computed(() => route.name === 'analytics' ? 'Analytics' : route.name === 'controls' ? 'Controls' : 'Dashboard')
</script>

<template>
  <header class="sticky top-0 z-30 border-b border-border/70 bg-background/90 px-4 backdrop-blur sm:px-6 lg:px-8">
    <div class="mx-auto flex h-16 max-w-[1500px] items-center justify-between">
      <div class="flex items-center gap-3">
        <button class="rounded-xl p-2 text-muted-foreground hover:bg-card lg:hidden" aria-label="Open menu" @click="$emit('openMenu')"><Menu :size="21" /></button>
        <div><p class="text-[11px] font-bold uppercase tracking-[0.15em] text-primary">Indoor environment</p><h1 class="text-lg font-bold tracking-tight text-foreground">{{ title }}</h1></div>
      </div>
      <div class="flex items-center gap-2 rounded-full border border-border bg-card px-3 py-2 text-xs font-semibold text-muted-foreground shadow-sm"><span class="h-2 w-2 rounded-full bg-success" />Edge API</div>
    </div>
  </header>
</template>
