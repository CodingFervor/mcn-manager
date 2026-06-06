import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(uni.getStorageSync('access_token') || '')
  const refreshToken = ref(uni.getStorageSync('refresh_token') || '')
  const employee = ref(JSON.parse(uni.getStorageSync('employee') || 'null'))

  const isLoggedIn = computed(() => !!accessToken.value)
  const employeeName = computed(() => employee.value?.name || '未登录')
  const employeeRole = computed(() => employee.value?.role || '')

  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    uni.setStorageSync('access_token', access)
    uni.setStorageSync('refresh_token', refresh)
  }

  function setEmployee(emp) {
    employee.value = emp
    uni.setStorageSync('employee', JSON.stringify(emp))
  }

  function clear() {
    accessToken.value = ''
    refreshToken.value = ''
    employee.value = null
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('refresh_token')
    uni.removeStorageSync('employee')
  }

  return {
    accessToken, refreshToken, employee,
    isLoggedIn, employeeName, employeeRole,
    setTokens, setEmployee, clear,
  }
})
