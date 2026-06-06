const BASE_URL = 'http://localhost:8000/api'

function getToken() {
  return uni.getStorageSync('access_token') || ''
}

function getRefreshToken() {
  return uni.getStorageSync('refresh_token') || ''
}

function request(options) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.header,
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          refreshToken().then(() => {
            request(options).then(resolve).catch(reject)
          }).catch(() => {
            uni.removeStorageSync('access_token')
            uni.removeStorageSync('refresh_token')
            uni.reLaunch({ url: '/pages/login/index' })
            reject(res)
          })
        } else {
          uni.showToast({ title: res.data?.detail || '请求失败', icon: 'none' })
          reject(res)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络异常', icon: 'none' })
        reject(err)
      },
    })
  })
}

function refreshToken() {
  return new Promise((resolve, reject) => {
    const refresh = getRefreshToken()
    if (!refresh) { reject(); return }
    uni.request({
      url: BASE_URL + '/auth/refresh/',
      method: 'POST',
      data: { refresh },
      success: (res) => {
        if (res.statusCode === 200) {
          uni.setStorageSync('access_token', res.data.access)
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: reject,
    })
  })
}

export const http = {
  get: (url, data) => request({ url, method: 'GET', data }),
  post: (url, data) => request({ url, method: 'POST', data }),
  put: (url, data) => request({ url, method: 'PUT', data }),
  delete: (url) => request({ url, method: 'DELETE' }),
}

export default http
