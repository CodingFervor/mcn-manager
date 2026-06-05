import { defineStore } from 'pinia'
import { ref } from 'vue'
import { DashboardAPI } from '../api'

export const useAppStore = defineStore('app', () => {
  const dashboard = ref(null)
  const loading = ref(false)
  const lastFetch = ref(0)
  const CACHE_TTL = 30_000

  async function fetchDashboard(force = false) {
    const now = Date.now()
    if (!force && dashboard.value && now - lastFetch.value < CACHE_TTL) {
      return dashboard.value
    }
    loading.value = true
    try {
      dashboard.value = await DashboardAPI.overview()
      lastFetch.value = now
      return dashboard.value
    } finally {
      loading.value = false
    }
  }

  function invalidateDashboard() {
    dashboard.value = null
    lastFetch.value = 0
  }

  return { dashboard, loading, fetchDashboard, invalidateDashboard }
})
