import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue'), meta: { title: '数据驾驶舱' } },
  { path: '/ai', name: 'ai', component: () => import('../views/AI.vue'), meta: { title: 'AI智能中心' } },
  { path: '/stores', name: 'stores', component: () => import('../views/Stores.vue'), meta: { title: '店铺管理' } },
  { path: '/employees', name: 'employees', component: () => import('../views/Employees.vue'), meta: { title: '人员管理' } },
  { path: '/schedules', name: 'schedules', component: () => import('../views/Schedules.vue'), meta: { title: '智能排班' } },
  { path: '/attendance', name: 'attendance', component: () => import('../views/Attendance.vue'), meta: { title: '考勤打卡' } },
  { path: '/sessions', name: 'sessions', component: () => import('../views/Sessions.vue'), meta: { title: '直播业绩' } },
  { path: '/reviews', name: 'reviews', component: () => import('../views/Reviews.vue'), meta: { title: '绩效考核' } },
  { path: '/shifts', name: 'shifts', component: () => import('../views/Shifts.vue'), meta: { title: '班次配置' } },
  // 20个新功能
  { path: '/products', name: 'products', component: () => import('../views/Products.vue'), meta: { title: '商品管理' } },
  { path: '/scripts', name: 'scripts', component: () => import('../views/Scripts.vue'), meta: { title: '直播工具' } },
  { path: '/tasks', name: 'tasks', component: () => import('../views/Tasks.vue'), meta: { title: '任务看板' } },
  { path: '/notifications', name: 'notifications', component: () => import('../views/Notifications.vue'), meta: { title: '消息中心' } },
  { path: '/finance', name: 'finance', component: () => import('../views/Finance.vue'), meta: { title: '财务中心' } },
  { path: '/training', name: 'training', component: () => import('../views/Training.vue'), meta: { title: '培训与目标' } },
  { path: '/competitor', name: 'competitor', component: () => import('../views/Competitor.vue'), meta: { title: '竞品与粉丝' } },
  { path: '/campaigns', name: 'campaigns', component: () => import('../views/Campaigns.vue'), meta: { title: '营销活动' } },
  { path: '/kol', name: 'kol', component: () => import('../views/KOL.vue'), meta: { title: '达人对接' } },
  { path: '/billboard', name: 'billboard', component: () => import('../views/Billboard.vue'), meta: { title: '实时大屏' } },
  { path: '/settings', name: 'settings', component: () => import('../views/Settings.vue'), meta: { title: '系统工具' } },
  // 10个新功能
  { path: '/stream-alerts', name: 'stream-alerts', component: () => import('../views/StreamAlerts.vue'), meta: { title: '直播监控' } },
  { path: '/assets', name: 'assets', component: () => import('../views/Assets.vue'), meta: { title: '设备资产' } },
  { path: '/knowledge', name: 'knowledge', component: () => import('../views/Knowledge.vue'), meta: { title: '知识库' } },
  { path: '/expenses', name: 'expenses', component: () => import('../views/Expenses.vue'), meta: { title: '费用报销' } },
  { path: '/complaints', name: 'complaints', component: () => import('../views/Complaints.vue'), meta: { title: '客户投诉' } },
  { path: '/stream-plans', name: 'stream-plans', component: () => import('../views/StreamPlans.vue'), meta: { title: '直播预告' } },
  { path: '/gifts', name: 'gifts', component: () => import('../views/Gifts.vue'), meta: { title: '打赏统计' } },
  { path: '/fan-groups', name: 'fan-groups', component: () => import('../views/FanGroups.vue'), meta: { title: '粉丝群' } },
  { path: '/reports', name: 'reports', component: () => import('../views/Reports.vue'), meta: { title: '数据报表' } },
  { path: '/suppliers', name: 'suppliers', component: () => import('../views/Suppliers.vue'), meta: { title: '供应商' } },
  // 10个业务功能
  { path: '/selections', name: 'selections', component: () => import('../views/Selections.vue'), meta: { title: '选品管理' } },
  { path: '/samples', name: 'samples', component: () => import('../views/Samples.vue'), meta: { title: '样品管理' } },
  { path: '/ad-campaigns', name: 'ad-campaigns', component: () => import('../views/AdCampaigns.vue'), meta: { title: '流量投放' } },
  { path: '/short-videos', name: 'short-videos', component: () => import('../views/ShortVideos.vue'), meta: { title: '短视频管理' } },
  { path: '/compliance', name: 'compliance', component: () => import('../views/Compliance.vue'), meta: { title: '合规审核' } },
  { path: '/opinions', name: 'opinions', component: () => import('../views/Opinions.vue'), meta: { title: '舆情监控' } },
  { path: '/after-sales', name: 'after-sales', component: () => import('../views/AfterSales.vue'), meta: { title: '售后工单' } },
  { path: '/revenue-sharing', name: 'revenue-sharing', component: () => import('../views/RevenueSharing.vue'), meta: { title: 'MCN分成' } },
  { path: '/brand-projects', name: 'brand-projects', component: () => import('../views/BrandProjects.vue'), meta: { title: '品牌合作' } },
  { path: '/scenes', name: 'scenes', component: () => import('../views/Scenes.vue'), meta: { title: '直播场景' } },
  // 第四轮 20个新功能
  { path: '/live-interactions', name: 'live-interactions', component: () => import('../views/LiveInteractions.vue'), meta: { title: '直播间互动' } },
  { path: '/coupons', name: 'coupons', component: () => import('../views/Coupons.vue'), meta: { title: '优惠券管理' } },
  { path: '/flash-sales', name: 'flash-sales', component: () => import('../views/FlashSales.vue'), meta: { title: '秒杀活动' } },
  { path: '/room-decorations', name: 'room-decorations', component: () => import('../views/RoomDecorations.vue'), meta: { title: '直播间装修' } },
  { path: '/script-tags', name: 'script-tags', component: () => import('../views/ScriptTags.vue'), meta: { title: '话术标签库' } },
  { path: '/sign-contracts', name: 'sign-contracts', component: () => import('../views/SignContracts.vue'), meta: { title: 'MCN签约' } },
  { path: '/negotiations', name: 'negotiations', component: () => import('../views/Negotiations.vue'), meta: { title: '商务洽谈' } },
  { path: '/investments', name: 'investments', component: () => import('../views/Investments.vue'), meta: { title: '招商管理' } },
  { path: '/contract-ledger', name: 'contract-ledger', component: () => import('../views/ContractLedger.vue'), meta: { title: '合同台账' } },
  { path: '/authorizations', name: 'authorizations', component: () => import('../views/Authorizations.vue'), meta: { title: '授权管理' } },
  { path: '/competitor-rooms', name: 'competitor-rooms', component: () => import('../views/CompetitorRooms.vue'), meta: { title: '竞品直播间' } },
  { path: '/traffic', name: 'traffic', component: () => import('../views/Traffic.vue'), meta: { title: '流量分析' } },
  { path: '/user-personas', name: 'user-personas', component: () => import('../views/UserPersonas.vue'), meta: { title: '用户画像' } },
  { path: '/ab-tests', name: 'ab-tests', component: () => import('../views/ABTests.vue'), meta: { title: 'AB测试' } },
  { path: '/data-warnings', name: 'data-warnings', component: () => import('../views/DataWarnings.vue'), meta: { title: '数据预警' } },
  { path: '/settlements', name: 'settlements', component: () => import('../views/Settlements.vue'), meta: { title: '结算单' } },
  { path: '/logistics', name: 'logistics', component: () => import('../views/Logistics.vue'), meta: { title: '物流跟踪' } },
  { path: '/inventories', name: 'inventories', component: () => import('../views/Inventories.vue'), meta: { title: '库存管理' } },
  { path: '/return-analysis', name: 'return-analysis', component: () => import('../views/ReturnAnalysis.vue'), meta: { title: '退货分析' } },
  { path: '/tax-records', name: 'tax-records', component: () => import('../views/TaxRecords.vue'), meta: { title: '税务管理' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'MCN管家'} - MCN 管家`
})

export default router
