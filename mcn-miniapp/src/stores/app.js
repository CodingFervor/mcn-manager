import { defineStore } from 'pinia'
import { ref } from 'vue'
import { DashboardAPI } from '@/api'

export const useAppStore = defineStore('app', () => {
  const dashboard = ref(null)
  const loading = ref(false)
  let lastFetch = 0
  const CACHE_TTL = 30000

  async function fetchDashboard(force = false) {
    const now = Date.now()
    if (!force && dashboard.value && now - lastFetch < CACHE_TTL) return dashboard.value
    loading.value = true
    try {
      const res = await DashboardAPI.overview()
      dashboard.value = res
      lastFetch = now
      return res
    } finally {
      loading.value = false
    }
  }

  return { dashboard, loading, fetchDashboard }
})
