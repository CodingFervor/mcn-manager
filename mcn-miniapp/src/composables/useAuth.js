import { useAuthStore } from '@/stores/auth'
import { AuthAPI } from '@/api'

export function useAuth() {
  const store = useAuthStore()

  async function wxLogin() {
    try {
      const [, loginRes] = await uni.login({ provider: 'weixin' })
      if (!loginRes || !loginRes.code) {
        uni.showToast({ title: '微信登录失败', icon: 'none' })
        return false
      }
      const res = await AuthAPI.wechatLogin(loginRes.code)
      store.setTokens(res.access, res.refresh)
      if (res.employee) {
        store.setEmployee(res.employee)
      }
      if (res.is_new || !res.employee) {
        uni.redirectTo({ url: '/pages/login/phone' })
      } else {
        uni.switchTab({ url: '/pages/dashboard/index' })
      }
      return true
    } catch (e) {
      console.error('wxLogin error', e)
      uni.showToast({ title: '登录失败', icon: 'none' })
      return false
    }
  }

  async function passwordLogin(username, password) {
    try {
      const res = await AuthAPI.login(username, password)
      store.setTokens(res.access, res.refresh)
      return true
    } catch (e) {
      uni.showToast({ title: '账号或密码错误', icon: 'none' })
      return false
    }
  }

  async function bindPhone(phone) {
    try {
      const res = await AuthAPI.bindPhone({ phone, encrypted_data: '', iv: '' })
      if (res.employee) {
        store.setEmployee(res.employee)
      }
      return res
    } catch (e) {
      uni.showToast({ title: '绑定失败', icon: 'none' })
      return null
    }
  }

  function logout() {
    store.clear()
    uni.reLaunch({ url: '/pages/login/index' })
  }

  return {
    wxLogin, passwordLogin, bindPhone, logout,
    isLoggedIn: store.isLoggedIn,
    employee: store.employee,
    employeeName: store.employeeName,
  }
}
