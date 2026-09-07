<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { BarChart3, LayoutDashboard, SlidersHorizontal, Wind, X } from '@lucide/vue'

defineProps<{ open: boolean }>()
defineEmits<{ close: [] }>()
const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Analytics', to: '/analytics', icon: BarChart3 },
  { name: 'Controls', to: '/controls', icon: SlidersHorizontal },
]
</script>

<template>
  <div v-if="open" class="fixed inset-0 z-40 bg-foreground/25 backdrop-blur-[1px] lg:hidden" @click="$emit('close')" />
  <aside class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-sidebar-border bg-sidebar px-4 py-5 transition-transform duration-200 lg:translate-x-0" :class="open ? 'translate-x-0' : '-translate-x-full'">
    <div class="flex items-center justify-between px-2">
      <RouterLink to="/" class="flex items-center gap-3" @click="$emit('close')">
        <span class="grid h-10 w-10 place-items-center rounded-2xl bg-primary text-primary-foreground shadow-sm"><Wind :size="21" :stroke-width="2.2" /></span>
        <span><span class="block text-lg font-bold tracking-tight text-foreground">Inhealth</span><span class="block text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">Edge monitor</span></span>
      </RouterLink>
      <button class="rounded-xl p-2 text-muted-foreground hover:bg-card lg:hidden" aria-label="Close menu" @click="$emit('close')"><X :size="20" /></button>
    </div>
    <nav class="mt-10 space-y-1.5">
      <RouterLink v-for="item in navigation" :key="item.name" :to="item.to" class="flex items-center gap-3 rounded-2xl px-3.5 py-3 text-sm font-semibold text-muted-foreground transition hover:bg-card/75 hover:text-primary" active-class="!bg-card !text-primary shadow-sm ring-1 ring-sidebar-border" @click="$emit('close')">
        <component :is="item.icon" :size="19" :stroke-width="2" />{{ item.name }}
      </RouterLink>
    </nav>
    <div class="mt-auto rounded-app border border-sidebar-border bg-card/70 p-4">
      <div class="flex items-center gap-2 text-xs font-semibold text-secondary-foreground"><span class="h-2 w-2 rounded-full bg-success ring-4 ring-success/10" />Edge architecture</div>
      <p class="mt-2 text-xs leading-5 text-muted-foreground">Arduino → MariaDB → FastAPI → dashboard</p>
    </div>
  </aside>
</template>
