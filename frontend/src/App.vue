<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppSidebar from './components/layout/AppSidebar.vue'

const sidebarOpen = ref(false)
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="lg:pl-64">
      <AppHeader @open-menu="sidebarOpen = true" />
      <main class="mx-auto max-w-[1500px] px-4 pb-10 pt-6 sm:px-6 lg:px-8 lg:pt-8">
        <RouterView />
      </main>
    </div>
  </div>
</template>
