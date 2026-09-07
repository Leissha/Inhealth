import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import ControlsView from '../views/ControlsView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView },
    { path: '/analytics', name: 'analytics', component: AnalyticsView },
    { path: '/controls', name: 'controls', component: ControlsView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

