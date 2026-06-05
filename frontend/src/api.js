import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

let loadingCount = 0

api.interceptors.request.use((config) => {
  loadingCount++
  return config
})

api.interceptors.response.use(
  (res) => {
    loadingCount--
    return res.data
  },
  (err) => {
    loadingCount--
    const msg = err.response?.data?.detail || err.response?.data?.message || err.message || '请求失败'
    if (err.response?.status !== 400) {
      ElMessage.error(msg)
    }
    return Promise.reject(err)
  },
)

const wrap = (promise) => promise.then((data) => (Array.isArray(data) ? data : data?.results || []))

export const BrandAPI = {
  list: () => wrap(api.get('/brands/')),
  create: (d) => api.post('/brands/', d),
  update: (id, d) => api.put(`/brands/${id}/`, d),
  remove: (id) => api.delete(`/brands/${id}/`),
}

export const StoreAPI = {
  list: (params) => wrap(api.get('/stores/', { params })),
  overview: (params) => api.get('/stores/overview/', { params }),
  create: (d) => api.post('/stores/', d),
  update: (id, d) => api.put(`/stores/${id}/`, d),
  remove: (id) => api.delete(`/stores/${id}/`),
}

export const TeamAPI = {
  list: () => wrap(api.get('/teams/')),
  create: (d) => api.post('/teams/', d),
  update: (id, d) => api.put(`/teams/${id}/`, d),
  remove: (id) => api.delete(`/teams/${id}/`),
}

export const RoomAPI = {
  list: (params) => wrap(api.get('/rooms/', { params })),
  create: (d) => api.post('/rooms/', d),
  remove: (id) => api.delete(`/rooms/${id}/`),
}

export const EmployeeAPI = {
  list: (params) => wrap(api.get('/employees/', { params })),
  stats: () => api.get('/employees/stats/'),
  create: (d) => api.post('/employees/', d),
  update: (id, d) => api.put(`/employees/${id}/`, d),
  remove: (id) => api.delete(`/employees/${id}/`),
}

export const ShiftAPI = {
  list: () => wrap(api.get('/shifts/')),
  create: (d) => api.post('/shifts/', d),
  update: (id, d) => api.put(`/shifts/${id}/`, d),
  remove: (id) => api.delete(`/shifts/${id}/`),
}

export const ScheduleAPI = {
  list: (params) => wrap(api.get('/schedules/', { params })),
  weekly: (params) => api.get('/schedules/weekly/', { params }),
  create: (d) => api.post('/schedules/', d),
  update: (id, d) => api.put(`/schedules/${id}/`, d),
  remove: (id) => api.delete(`/schedules/${id}/`),
  batchCreate: (data) => api.post('/schedules/batch_create/', data),
}

export const AttendanceAPI = {
  list: (params) => wrap(api.get('/attendances/', { params })),
  clockIn: (d) => api.post('/attendances/clock_in/', d),
  clockOut: (d) => api.post('/attendances/clock_out/', d),
  summary: (params) => api.get('/attendances/summary/', { params }),
}

export const LeaveAPI = {
  list: (params) => wrap(api.get('/leaves/', { params })),
  create: (d) => api.post('/leaves/', d),
  approve: (id, d) => api.post(`/leaves/${id}/approve/`, d),
  reject: (id, d) => api.post(`/leaves/${id}/reject/`, d),
}

export const SessionAPI = {
  list: (params) => wrap(api.get('/sessions/', { params })),
  dailyGmv: (params) => api.get('/sessions/daily_gmv/', { params }),
  topAnchors: (params) => api.get('/sessions/top_anchors/', { params }),
  create: (d) => api.post('/sessions/', d),
  update: (id, d) => api.put(`/sessions/${id}/`, d),
  remove: (id) => api.delete(`/sessions/${id}/`),
}

export const ReviewAPI = {
  list: (params) => wrap(api.get('/reviews/', { params })),
  calculate: (d) => api.post('/reviews/calculate/', d),
}

export const KPIConfigAPI = {
  list: () => wrap(api.get('/kpi-configs/')),
  create: (d) => api.post('/kpi-configs/', d),
  update: (id, d) => api.put(`/kpi-configs/${id}/`, d),
  remove: (id) => api.delete(`/kpi-configs/${id}/`),
}

export const DashboardAPI = {
  overview: () => api.get('/dashboard/overview/'),
}

export const AI_API = {
  predict: (params) => api.get('/ai/predict/', { params }),
  schedule: (params) => api.get('/ai/schedule/', { params }),
  anchor: (params) => api.get('/ai/anchor/', { params }),
  anomaly: (params) => api.get('/ai/anomaly/', { params }),
  insights: () => api.get('/ai/insights/'),
  match: (params) => api.get('/ai/match/', { params }),
}

// ===== 20 新功能 API =====
export const ProductAPI = {
  list: (params) => wrap(api.get('/products/', { params })),
  create: (d) => api.post('/products/', d),
  update: (id, d) => api.put(`/products/${id}/`, d),
  remove: (id) => api.delete(`/products/${id}/`),
}

export const ScriptAPI = {
  list: (params) => wrap(api.get('/stream-scripts/', { params })),
  create: (d) => api.post('/stream-scripts/', d),
  salesList: (params) => wrap(api.get('/sales-scripts/', { params })),
}

export const TaskAPI = {
  list: () => wrap(api.get('/task-boards/')),
  create: (d) => api.post('/task-boards/', d),
  createCard: (d) => api.post('/task-cards/', d),
  move: (id, d) => api.post(`/task-cards/${id}/move/`, d),
}

export const NotificationAPI = {
  list: (params) => wrap(api.get('/notifications/', { params })),
  readAll: (d) => api.post('/notifications/read_all/', d || {}),
  unreadCount: () => api.get('/notifications/unread_count/'),
}

export const FinanceAPI = {
  list: (params) => wrap(api.get('/finance/', { params })),
  summary: (params) => api.get('/finance/summary/', { params }),
}

export const ContractAPI = {
  list: (params) => wrap(api.get('/contracts/', { params })),
}

export const CommissionAPI = {
  list: (params) => wrap(api.get('/commissions/', { params })),
  settle: (id) => api.post(`/commissions/${id}/settle/`),
}

export const TrainingAPI = {
  list: (params) => wrap(api.get('/training-courses/', { params })),
}

export const GoalAPI = {
  board: (params) => api.get('/goals/board/', { params }),
}

export const CompetitorAPI = {
  list: (params) => wrap(api.get('/competitors/', { params })),
}

export const FanAPI = {
  trend: (params) => api.get('/fan-analysis/trend/', { params }),
}

export const CampaignAPI = {
  list: (params) => wrap(api.get('/campaigns/', { params })),
}

export const KOLAPI = {
  list: (params) => wrap(api.get('/kols/', { params })),
}

export const BillboardAPI = {
  data: () => api.get('/billboard/data/'),
}

export const ExportAPI = {
  list: () => wrap(api.get('/exports/')),
  create: (d) => api.post('/exports/create_export/', d),
}

// ===== 10 新功能 API =====
export const StreamAlertAPI = {
  list: (params) => wrap(api.get('/stream-alerts/', { params })),
  create: (d) => api.post('/stream-alerts/', d),
  update: (id, d) => api.put(`/stream-alerts/${id}/`, d),
  stats: () => api.get('/stream-alerts/stats/'),
  resolve: (id, d) => api.post(`/stream-alerts/${id}/resolve/`, d),
}

export const AssetAPI = {
  list: (params) => wrap(api.get('/assets/', { params })),
  create: (d) => api.post('/assets/', d),
  update: (id, d) => api.put(`/assets/${id}/`, d),
  remove: (id) => api.delete(`/assets/${id}/`),
  stats: () => api.get('/assets/stats/'),
  byCategory: () => api.get('/assets/by_category/'),
}

export const KnowledgeAPI = {
  list: (params) => wrap(api.get('/knowledge/', { params })),
  create: (d) => api.post('/knowledge/', d),
  update: (id, d) => api.put(`/knowledge/${id}/`, d),
  remove: (id) => api.delete(`/knowledge/${id}/`),
  publish: (id) => api.post(`/knowledge/${id}/publish/`),
  popular: () => api.get('/knowledge/popular/'),
}

export const ExpenseAPI = {
  list: (params) => wrap(api.get('/expenses/', { params })),
  create: (d) => api.post('/expenses/', d),
  update: (id, d) => api.put(`/expenses/${id}/`, d),
  stats: () => api.get('/expenses/stats/'),
  approve: (id, d) => api.post(`/expenses/${id}/approve/`, d),
  reject: (id, d) => api.post(`/expenses/${id}/reject/`, d),
}

export const ComplaintAPI = {
  list: (params) => wrap(api.get('/complaints/', { params })),
  create: (d) => api.post('/complaints/', d),
  update: (id, d) => api.put(`/complaints/${id}/`, d),
  stats: () => api.get('/complaints/stats/'),
  resolve: (id, d) => api.post(`/complaints/${id}/resolve/`, d),
}

export const StreamPlanAPI = {
  list: (params) => wrap(api.get('/stream-plans/', { params })),
  create: (d) => api.post('/stream-plans/', d),
  update: (id, d) => api.put(`/stream-plans/${id}/`, d),
  remove: (id) => api.delete(`/stream-plans/${id}/`),
  upcoming: () => api.get('/stream-plans/upcoming/'),
  calendar: (params) => api.get('/stream-plans/calendar/', { params }),
}

export const GiftAPI = {
  list: (params) => wrap(api.get('/gifts/', { params })),
  create: (d) => api.post('/gifts/', d),
  stats: () => api.get('/gifts/stats/'),
  bySession: (sessionId) => api.get('/gifts/by_session/', { params: { session_id: sessionId } }),
}

export const FanGroupAPI = {
  list: (params) => wrap(api.get('/fan-groups/', { params })),
  create: (d) => api.post('/fan-groups/', d),
  update: (id, d) => api.put(`/fan-groups/${id}/`, d),
  remove: (id) => api.delete(`/fan-groups/${id}/`),
  stats: () => api.get('/fan-groups/stats/'),
}

export const ReportAPI = {
  list: (params) => wrap(api.get('/reports/', { params })),
  create: (d) => api.post('/reports/', d),
  recent: () => api.get('/reports/recent/'),
  generate: (id) => api.post(`/reports/${id}/generate/`),
}

export const SupplierAPI = {
  list: (params) => wrap(api.get('/suppliers/', { params })),
  create: (d) => api.post('/suppliers/', d),
  update: (id, d) => api.put(`/suppliers/${id}/`, d),
  remove: (id) => api.delete(`/suppliers/${id}/`),
  stats: () => api.get('/suppliers/stats/'),
}

// ===== 10 业务功能 API =====
export const SelectionAPI = {
  list: (params) => wrap(api.get('/selections/', { params })),
  create: (d) => api.post('/selections/', d),
  update: (id, d) => api.put(`/selections/${id}/`, d),
  remove: (id) => api.delete(`/selections/${id}/`),
  stats: () => api.get('/selections/stats/'),
  topScored: () => api.get('/selections/top_scored/'),
}

export const SampleAPI = {
  list: (params) => wrap(api.get('/samples/', { params })),
  create: (d) => api.post('/samples/', d),
  update: (id, d) => api.put(`/samples/${id}/`, d),
  remove: (id) => api.delete(`/samples/${id}/`),
  stats: () => api.get('/samples/stats/'),
  receive: (id) => api.post(`/samples/${id}/receive/`),
  returnSample: (id) => api.post(`/samples/${id}/return_sample/`),
}

export const AdCampaignAPI = {
  list: (params) => wrap(api.get('/ad-campaigns/', { params })),
  create: (d) => api.post('/ad-campaigns/', d),
  update: (id, d) => api.put(`/ad-campaigns/${id}/`, d),
  remove: (id) => api.delete(`/ad-campaigns/${id}/`),
  stats: () => api.get('/ad-campaigns/stats/'),
  byPlatform: () => api.get('/ad-campaigns/by_platform/'),
}

export const ShortVideoAPI = {
  list: (params) => wrap(api.get('/short-videos/', { params })),
  create: (d) => api.post('/short-videos/', d),
  update: (id, d) => api.put(`/short-videos/${id}/`, d),
  remove: (id) => api.delete(`/short-videos/${id}/`),
  stats: () => api.get('/short-videos/stats/'),
  topPerforming: () => api.get('/short-videos/top_performing/'),
}

export const ComplianceAPI = {
  list: (params) => wrap(api.get('/compliance/', { params })),
  create: (d) => api.post('/compliance/', d),
  update: (id, d) => api.put(`/compliance/${id}/`, d),
  remove: (id) => api.delete(`/compliance/${id}/`),
  stats: () => api.get('/compliance/stats/'),
  approve: (id, d) => api.post(`/compliance/${id}/approve/`, d),
  reject: (id, d) => api.post(`/compliance/${id}/reject/`, d),
}

export const OpinionAPI = {
  list: (params) => wrap(api.get('/opinions/', { params })),
  create: (d) => api.post('/opinions/', d),
  update: (id, d) => api.put(`/opinions/${id}/`, d),
  stats: () => api.get('/opinions/stats/'),
  resolve: (id, d) => api.post(`/opinions/${id}/resolve/`, d),
}

export const AfterSalesAPI = {
  list: (params) => wrap(api.get('/after-sales/', { params })),
  create: (d) => api.post('/after-sales/', d),
  update: (id, d) => api.put(`/after-sales/${id}/`, d),
  stats: () => api.get('/after-sales/stats/'),
  approve: (id, d) => api.post(`/after-sales/${id}/approve/`, d),
  complete: (id, d) => api.post(`/after-sales/${id}/complete/`, d),
}

export const RevenueSharingAPI = {
  list: (params) => wrap(api.get('/revenue-sharing/', { params })),
  create: (d) => api.post('/revenue-sharing/', d),
  update: (id, d) => api.put(`/revenue-sharing/${id}/`, d),
  stats: () => api.get('/revenue-sharing/stats/'),
  settle: (id) => api.post(`/revenue-sharing/${id}/settle/`),
}

export const BrandProjectAPI = {
  list: (params) => wrap(api.get('/brand-projects/', { params })),
  create: (d) => api.post('/brand-projects/', d),
  update: (id, d) => api.put(`/brand-projects/${id}/`, d),
  remove: (id) => api.delete(`/brand-projects/${id}/`),
  stats: () => api.get('/brand-projects/stats/'),
  active: () => api.get('/brand-projects/active/'),
}

export const SceneAPI = {
  list: (params) => wrap(api.get('/scenes/', { params })),
  create: (d) => api.post('/scenes/', d),
  update: (id, d) => api.put(`/scenes/${id}/`, d),
  remove: (id) => api.delete(`/scenes/${id}/`),
  stats: () => api.get('/scenes/stats/'),
  activate: (id) => api.post(`/scenes/${id}/activate/`),
}

// ===== 第四轮 20 新功能 API =====

// 运营管理类
export const LiveInteractionAPI = {
  list: (params) => wrap(api.get('/live-interactions/', { params })),
  create: (d) => api.post('/live-interactions/', d),
  stats: () => api.get('/live-interactions/stats/'),
  bySession: (sessionId) => api.get('/live-interactions/by_session/', { params: { session_id: sessionId } }),
}

export const CouponAPI = {
  list: (params) => wrap(api.get('/coupons/', { params })),
  create: (d) => api.post('/coupons/', d),
  update: (id, d) => api.put(`/coupons/${id}/`, d),
  remove: (id) => api.delete(`/coupons/${id}/`),
  stats: () => api.get('/coupons/stats/'),
  activate: (id) => api.post(`/coupons/${id}/activate/`),
}

export const FlashSaleAPI = {
  list: (params) => wrap(api.get('/flash-sales/', { params })),
  create: (d) => api.post('/flash-sales/', d),
  update: (id, d) => api.put(`/flash-sales/${id}/`, d),
  remove: (id) => api.delete(`/flash-sales/${id}/`),
  stats: () => api.get('/flash-sales/stats/'),
  upcoming: () => api.get('/flash-sales/upcoming/'),
}

export const RoomDecorationAPI = {
  list: (params) => wrap(api.get('/room-decorations/', { params })),
  create: (d) => api.post('/room-decorations/', d),
  update: (id, d) => api.put(`/room-decorations/${id}/`, d),
  remove: (id) => api.delete(`/room-decorations/${id}/`),
  stats: () => api.get('/room-decorations/stats/'),
  toggle: (id) => api.post(`/room-decorations/${id}/toggle/`),
}

export const ScriptTagAPI = {
  list: (params) => wrap(api.get('/script-tags/', { params })),
  create: (d) => api.post('/script-tags/', d),
  update: (id, d) => api.put(`/script-tags/${id}/`, d),
  remove: (id) => api.delete(`/script-tags/${id}/`),
  stats: () => api.get('/script-tags/stats/'),
  tree: () => api.get('/script-tags/tree/'),
}

// 商务拓展类
export const SignContractAPI = {
  list: (params) => wrap(api.get('/sign-contracts/', { params })),
  create: (d) => api.post('/sign-contracts/', d),
  update: (id, d) => api.put(`/sign-contracts/${id}/`, d),
  stats: () => api.get('/sign-contracts/stats/'),
  approve: (id) => api.post(`/sign-contracts/${id}/approve/`),
  terminate: (id) => api.post(`/sign-contracts/${id}/terminate/`),
}

export const NegotiationAPI = {
  list: (params) => wrap(api.get('/negotiations/', { params })),
  create: (d) => api.post('/negotiations/', d),
  update: (id, d) => api.put(`/negotiations/${id}/`, d),
  remove: (id) => api.delete(`/negotiations/${id}/`),
  stats: () => api.get('/negotiations/stats/'),
  pipeline: () => api.get('/negotiations/pipeline/'),
}

export const InvestmentAPI = {
  list: (params) => wrap(api.get('/investments/', { params })),
  create: (d) => api.post('/investments/', d),
  update: (id, d) => api.put(`/investments/${id}/`, d),
  remove: (id) => api.delete(`/investments/${id}/`),
  stats: () => api.get('/investments/stats/'),
  topProspects: () => api.get('/investments/top_prospects/'),
}

export const ContractLedgerAPI = {
  list: (params) => wrap(api.get('/contract-ledger/', { params })),
  create: (d) => api.post('/contract-ledger/', d),
  update: (id, d) => api.put(`/contract-ledger/${id}/`, d),
  remove: (id) => api.delete(`/contract-ledger/${id}/`),
  stats: () => api.get('/contract-ledger/stats/'),
  expiring: (days) => api.get('/contract-ledger/expiring/', { params: { days } }),
}

export const AuthorizationAPI = {
  list: (params) => wrap(api.get('/authorizations/', { params })),
  create: (d) => api.post('/authorizations/', d),
  update: (id, d) => api.put(`/authorizations/${id}/`, d),
  remove: (id) => api.delete(`/authorizations/${id}/`),
  stats: () => api.get('/authorizations/stats/'),
  expiring: (days) => api.get('/authorizations/expiring/', { params: { days } }),
}

// 数据与策略类
export const CompetitorRoomAPI = {
  list: (params) => wrap(api.get('/competitor-rooms/', { params })),
  create: (d) => api.post('/competitor-rooms/', d),
  update: (id, d) => api.put(`/competitor-rooms/${id}/`, d),
  remove: (id) => api.delete(`/competitor-rooms/${id}/`),
  stats: () => api.get('/competitor-rooms/stats/'),
  ranking: () => api.get('/competitor-rooms/ranking/'),
}

export const TrafficAPI = {
  list: (params) => wrap(api.get('/traffic-analysis/', { params })),
  create: (d) => api.post('/traffic-analysis/', d),
  stats: () => api.get('/traffic-analysis/stats/'),
  bySource: () => api.get('/traffic-analysis/by_source/'),
}

export const UserPersonaAPI = {
  list: (params) => wrap(api.get('/user-personas/', { params })),
  create: (d) => api.post('/user-personas/', d),
  update: (id, d) => api.put(`/user-personas/${id}/`, d),
  remove: (id) => api.delete(`/user-personas/${id}/`),
  stats: () => api.get('/user-personas/stats/'),
  vips: () => api.get('/user-personas/vips/'),
}

export const ABTestAPI = {
  list: (params) => wrap(api.get('/ab-tests/', { params })),
  create: (d) => api.post('/ab-tests/', d),
  update: (id, d) => api.put(`/ab-tests/${id}/`, d),
  stats: () => api.get('/ab-tests/stats/'),
  complete: (id) => api.post(`/ab-tests/${id}/complete/`),
}

export const DataWarningAPI = {
  list: (params) => wrap(api.get('/data-warnings/', { params })),
  create: (d) => api.post('/data-warnings/', d),
  update: (id, d) => api.put(`/data-warnings/${id}/`, d),
  remove: (id) => api.delete(`/data-warnings/${id}/`),
  stats: () => api.get('/data-warnings/stats/'),
  toggle: (id) => api.post(`/data-warnings/${id}/toggle/`),
}

// 财务与供应链类
export const SettlementAPI = {
  list: (params) => wrap(api.get('/settlements/', { params })),
  create: (d) => api.post('/settlements/', d),
  update: (id, d) => api.put(`/settlements/${id}/`, d),
  stats: () => api.get('/settlements/stats/'),
  approve: (id) => api.post(`/settlements/${id}/approve/`),
  pay: (id) => api.post(`/settlements/${id}/pay/`),
}

export const LogisticsAPI = {
  list: (params) => wrap(api.get('/logistics/', { params })),
  create: (d) => api.post('/logistics/', d),
  update: (id, d) => api.put(`/logistics/${id}/`, d),
  stats: () => api.get('/logistics/stats/'),
  ship: (id) => api.post(`/logistics/${id}/ship/`),
  deliver: (id) => api.post(`/logistics/${id}/deliver/`),
}

export const InventoryAPI = {
  list: (params) => wrap(api.get('/inventories/', { params })),
  create: (d) => api.post('/inventories/', d),
  update: (id, d) => api.put(`/inventories/${id}/`, d),
  remove: (id) => api.delete(`/inventories/${id}/`),
  stats: () => api.get('/inventories/stats/'),
  lowStock: () => api.get('/inventories/low_stock/'),
  restock: (id, qty) => api.post(`/inventories/${id}/restock/`, { quantity: qty }),
}

export const ReturnAnalysisAPI = {
  list: (params) => wrap(api.get('/return-analysis/', { params })),
  create: (d) => api.post('/return-analysis/', d),
  update: (id, d) => api.put(`/return-analysis/${id}/`, d),
  stats: () => api.get('/return-analysis/stats/'),
  resolve: (id, d) => api.post(`/return-analysis/${id}/resolve/`, d),
}

export const TaxRecordAPI = {
  list: (params) => wrap(api.get('/tax-records/', { params })),
  create: (d) => api.post('/tax-records/', d),
  update: (id, d) => api.put(`/tax-records/${id}/`, d),
  remove: (id) => api.delete(`/tax-records/${id}/`),
  stats: () => api.get('/tax-records/stats/'),
  byPeriod: (period) => api.get('/tax-records/by_period/', { params: { period } }),
}
