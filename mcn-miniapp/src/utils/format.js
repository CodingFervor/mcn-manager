import dayjs from 'dayjs'

export function formatMoney(value) {
  if (value == null) return '¥0'
  const num = Number(value)
  if (num >= 10000) return `¥${(num / 10000).toFixed(1)}万`
  return `¥${num.toFixed(2)}`
}

export function formatDate(date, fmt = 'YYYY-MM-DD') {
  if (!date) return ''
  return dayjs(date).format(fmt)
}

export function formatDateTime(date) {
  return formatDate(date, 'MM-DD HH:mm')
}

export function formatTime(date) {
  return formatDate(date, 'HH:mm')
}

export function formatPercent(value) {
  if (value == null) return '0%'
  return `${Number(value).toFixed(1)}%`
}

export function getStatusClass(status) {
  const map = {
    active: 'status-active', ongoing: 'status-active', completed: 'status-active',
    approved: 'status-active', paid: 'status-active',
    pending: 'status-pending', draft: 'status-pending', scheduled: 'status-pending',
    inactive: 'status-inactive', cancelled: 'status-inactive', rejected: 'status-inactive',
    overdue: 'status-danger', urgent: 'status-danger', failed: 'status-danger',
  }
  return map[status] || 'status-inactive'
}

export function getStatusText(status) {
  const map = {
    active: '进行中', pending: '待处理', completed: '已完成',
    approved: '已审批', rejected: '已拒绝', cancelled: '已取消',
    draft: '草稿', scheduled: '已排期', ongoing: '进行中',
    inactive: '未激活', overdue: '已逾期', urgent: '紧急',
    paid: '已支付', failed: '失败',
  }
  return map[status] || status
}
