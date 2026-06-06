import http from '@/utils/request'

const API_BASE = ''

export const AuthAPI = {
  wechatLogin: (code) => http.post(`${API_BASE}/auth/wechat-login/`, { code }),
  login: (username, password) => http.post(`${API_BASE}/auth/login/`, { username, password }),
  bindPhone: (data) => http.post(`${API_BASE}/auth/wechat-phone/`, data),
}

export const DashboardAPI = {
  overview: () => http.get(`${API_BASE}/dashboard/stats/`),
}

export const ScheduleAPI = {
  list: (params) => http.get('/schedules/', params),
  today: () => http.get('/schedules/', { date: 'today' }),
}

export const AttendanceAPI = {
  list: (params) => http.get('/attendances/', params),
  clockIn: (data) => http.post('/attendances/clock_in/', data),
  clockOut: (data) => http.post('/attendances/clock_out/', data),
  summary: () => http.get('/attendances/summary/'),
}

export const SessionAPI = {
  list: (params) => http.get('/live-sessions/', params),
  detail: (id) => http.get(`/live-sessions/${id}/`),
}

export const TaskAPI = {
  boards: () => http.get('/task-boards/'),
  list: (params) => http.get('/task-cards/', params),
  create: (data) => http.post('/task-cards/', data),
  update: (id, data) => http.put(`/task-cards/${id}/`, data),
}

export const NotificationAPI = {
  list: (params) => http.get('/notifications/', params),
  readAll: () => http.post('/notifications/read_all/'),
  unreadCount: () => http.get('/notifications/unread_count/'),
}

export const EmployeeAPI = {
  myProfile: () => http.get('/employees/my_profile/'),
  list: (params) => http.get('/employees/', params),
}

export const StreamPlanAPI = {
  list: (params) => http.get('/stream-plans/', params),
  upcoming: () => http.get('/stream-plans/', { status: 'upcoming' }),
}

export const StreamChecklistAPI = {
  list: (params) => http.get('/stream-checklists/', params),
  update: (id, data) => http.put(`/stream-checklists/${id}/`, data),
}

export const ProductAPI = {
  list: (params) => http.get('/products/', params),
}

export const OrderAPI = {
  list: (params) => http.get('/orders/', params),
}

export const SalesTargetAPI = {
  list: (params) => http.get('/sales-targets/', params),
}

export const FinanceAPI = {
  list: (params) => http.get('/finance-records/', params),
  summary: () => http.get('/finance-records/stats/'),
}

export const TeamChatAPI = {
  list: (params) => http.get('/team-communications/', params),
}

export const KnowledgeAPI = {
  list: (params) => http.get('/knowledge-documents/', params),
  detail: (id) => http.get(`/knowledge-documents/${id}/`),
}

export const TrainingAPI = {
  list: (params) => http.get('/training-courses/', params),
}

export const ComplaintAPI = {
  list: (params) => http.get('/complaints/', params),
  resolve: (id, data) => http.post(`/complaints/${id}/resolve/`, data),
}

export const ExpenseAPI = {
  list: (params) => http.get('/expenses/', params),
  create: (data) => http.post('/expenses/', data),
}

export const ReviewAPI = {
  list: (params) => http.get('/performance-reviews/', params),
  calculate: (data) => http.post('/performance-reviews/calculate/', data),
}

export const LeaveAPI = {
  list: (params) => http.get('/leaves/', params),
  create: (data) => http.post('/leaves/', data),
}

export const StoreAPI = {
  list: (params) => http.get('/stores/', params),
}

export const ShiftAPI = {
  list: (params) => http.get('/shifts/', params),
}

export const GiftAPI = {
  list: (params) => http.get('/gift-records/', params),
}

export const CommissionAPI = {
  list: (params) => http.get('/commissions/', params),
}

// Enterprise APIs
export const SystemAnnouncementAPI = {
  list: (params) => http.get('/system-announcements/', params),
  create: (data) => http.post('/system-announcements/', data),
}
export const PermissionPolicyAPI = {
  list: (params) => http.get('/permission-policies/', params),
}
export const AuditLogAPI = {
  list: (params) => http.get('/audit-logs/', params),
}
export const DataBackupAPI = {
  list: (params) => http.get('/data-backups/', params),
  run: (id) => http.post(`/data-backups/${id}/run_backup/`),
}
export const HealthMonitorAPI = {
  list: (params) => http.get('/health-monitors/', params),
  check: (id) => http.post(`/health-monitors/${id}/check_health/`),
}
export const IntegrationConfigAPI = {
  list: (params) => http.get('/integration-configs/', params),
}
export const WorkflowTemplateAPI = {
  list: (params) => http.get('/workflow-templates/', params),
}
export const NotificationTemplateAPI = {
  list: (params) => http.get('/notification-templates/', params),
}
export const ReportSchedulerAPI = {
  list: (params) => http.get('/report-schedulers/', params),
}
export const ExportCenterAPI = {
  list: (params) => http.get('/export-center/', params),
  start: (data) => http.post('/export-center/start_export/', data),
}
export const WhiteLabelConfigAPI = {
  list: (params) => http.get('/white-label-configs/', params),
}
export const MultiTenantConfigAPI = {
  list: (params) => http.get('/multi-tenant-configs/', params),
}
export const LicenseManagementAPI = {
  list: (params) => http.get('/license-management/', params),
}
export const RiskAssessmentAPI = {
  list: (params) => http.get('/risk-assessments/', params),
}
export const DisasterRecoveryAPI = {
  list: (params) => http.get('/disaster-recoveries/', params),
}
export const ComplianceAuditAPI = {
  list: (params) => http.get('/compliance-audits/', params),
}
export const SystemConfigAPI = {
  list: (params) => http.get('/system-configs/', params),
  update: (id, data) => http.put(`/system-configs/${id}/`, data),
}
export const FeatureFlagAPI = {
  list: (params) => http.get('/feature-flags/', params),
  update: (id, data) => http.put(`/feature-flags/${id}/`, data),
}
export const ApiKeyManagementAPI = {
  list: (params) => http.get('/api-key-managements/', params),
}
export const DeploymentRecordAPI = {
  list: (params) => http.get('/deployment-records/', params),
}
