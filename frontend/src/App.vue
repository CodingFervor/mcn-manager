<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  DataLine, Shop, User, Clock, Calendar, VideoCamera,
  Trophy, Setting, Bell, Search, MagicStick, Goods, Tickets,
  Notebook, ChatDotRound, Money, Reading, DataBoard,
  Promotion, UserFilled, Monitor, Warning, Box, Document,
  Wallet, Service, Flag, Present, Connection, DataAnalysis, Phone,
  Star, Opportunity, Film, Lock, ChatLineSquare, Ticket,
  Histogram, OfficeBuilding, Picture,
  ChatRound, PriceTag, Timer, Brush, Collection,
  Files, Coordinate, House, Stamp, Key,
  View, TrendCharts, Avatar, Aim, AlarmClock,
  List, Van, Grid, RefreshLeft, WalletFilled, Fold,
  CircleCheck, VideoPlay, Link, CopyDocument, PictureFilled,
  ShoppingCart, CreditCard, Message, Share, Checked, Lock as Shield, ChatLineSquare as Comment,
  Notification, Tools, DocumentCopy, Upload, Monitor as HeartMonitor,
  Position, Operation, Bell as BellTemplate, Timer as ReportTimer,
  Download, Brush as WhiteLabelBrush, House as TenantHouse,
  Key as LicenseKey, Warning as RiskWarning, RefreshLeft as DRRecovery,
  CircleCheck as AuditCheck, Setting as SysSetting,
  Open, Key as ApiKey, Upload as DeployUpload
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const isMobile = ref(false)
const drawerVisible = ref(false)
const active = computed(() => route.path.slice(1) || 'dashboard')
const currentTime = ref('')

const menuItems = [
  { index: 'dashboard', label: '数据驾驶舱', icon: DataLine, badge: 'HOT' },
  { index: 'billboard', label: '实时大屏', icon: Monitor },
  { index: 'ai', label: 'AI 智能中心', icon: MagicStick, badge: 'AI' },
  { index: 'stores', label: '店铺管理', icon: Shop },
  { index: 'employees', label: '人员管理', icon: User },
  { index: 'products', label: '商品管理', icon: Goods },
  { index: 'schedules', label: '智能排班', icon: Calendar },
  { index: 'attendance', label: '考勤打卡', icon: Clock },
  { index: 'sessions', label: '直播业绩', icon: VideoCamera },
  { index: 'scripts', label: '直播工具', icon: Tickets },
  { index: 'reviews', label: '绩效考核', icon: Trophy },
  { index: 'finance', label: '财务中心', icon: Money },
  { index: 'campaigns', label: '营销活动', icon: Promotion },
  { index: 'tasks', label: '任务看板', icon: Notebook },
  { index: 'notifications', label: '消息中心', icon: Bell },
  { index: 'competitor', label: '竞品与粉丝', icon: DataBoard },
  { index: 'kol', label: '达人对接', icon: UserFilled },
  { index: 'training', label: '培训与目标', icon: Reading },
  { index: 'shifts', label: '班次配置', icon: Setting },
  { index: 'settings', label: '系统工具', icon: ChatDotRound },
  { index: 'stream-alerts', label: '直播监控', icon: Warning },
  { index: 'assets', label: '设备资产', icon: Box },
  { index: 'knowledge', label: '知识库', icon: Document },
  { index: 'expenses', label: '费用报销', icon: Wallet },
  { index: 'complaints', label: '客户投诉', icon: Service },
  { index: 'stream-plans', label: '直播预告', icon: Flag },
  { index: 'gifts', label: '打赏统计', icon: Present },
  { index: 'fan-groups', label: '粉丝群', icon: Connection },
  { index: 'reports', label: '数据报表', icon: DataAnalysis },
  { index: 'suppliers', label: '供应商', icon: Phone },
  { index: 'selections', label: '选品管理', icon: Star },
  { index: 'samples', label: '样品管理', icon: Box },
  { index: 'ad-campaigns', label: '流量投放', icon: Opportunity },
  { index: 'short-videos', label: '短视频管理', icon: Film },
  { index: 'compliance', label: '合规审核', icon: Lock },
  { index: 'opinions', label: '舆情监控', icon: ChatLineSquare },
  { index: 'after-sales', label: '售后工单', icon: Ticket },
  { index: 'revenue-sharing', label: 'MCN分成', icon: Histogram },
  { index: 'brand-projects', label: '品牌合作', icon: OfficeBuilding },
  { index: 'scenes', label: '直播场景', icon: Picture },
  { index: 'live-interactions', label: '直播间互动', icon: ChatRound },
  { index: 'coupons', label: '优惠券管理', icon: PriceTag },
  { index: 'flash-sales', label: '秒杀活动', icon: Timer },
  { index: 'room-decorations', label: '直播间装修', icon: Brush },
  { index: 'script-tags', label: '话术标签库', icon: Collection },
  { index: 'sign-contracts', label: 'MCN签约', icon: Files },
  { index: 'negotiations', label: '商务洽谈', icon: Coordinate },
  { index: 'investments', label: '招商管理', icon: House },
  { index: 'contract-ledger', label: '合同台账', icon: Stamp },
  { index: 'authorizations', label: '授权管理', icon: Key },
  { index: 'competitor-rooms', label: '竞品直播间', icon: View },
  { index: 'traffic', label: '流量分析', icon: TrendCharts },
  { index: 'user-personas', label: '用户画像', icon: Avatar },
  { index: 'ab-tests', label: 'AB测试', icon: Aim },
  { index: 'data-warnings', label: '数据预警', icon: AlarmClock },
  { index: 'settlements', label: '结算单', icon: List },
  { index: 'logistics', label: '物流跟踪', icon: Van },
  { index: 'inventories', label: '库存管理', icon: Grid },
  { index: 'return-analysis', label: '退货分析', icon: RefreshLeft },
  { index: 'tax-records', label: '税务管理', icon: WalletFilled },
  // 第五轮 50个新功能
  { index: 'stream-checklists', label: '直播检查清单', icon: CircleCheck },
  { index: 'stream-replays', label: '直播回放', icon: VideoPlay },
  { index: 'stream-backups', label: '直播备用方案', icon: FirstAidKit },
  { index: 'stream-quality', label: '直播质量监控', icon: DataLine },
  { index: 'live-timelines', label: '直播时间轴', icon: Clock },
  { index: 'product-links', label: '商品链接', icon: Link },
  { index: 'stream-templates', label: '直播模板', icon: CopyDocument },
  { index: 'stream-overlays', label: '直播叠加层', icon: PictureFilled },
  { index: 'live-polls', label: '直播投票', icon: PieChart },
  { index: 'orders', label: '订单管理', icon: ShoppingCart },
  { index: 'refunds', label: '退款管理', icon: Tickets },
  { index: 'price-monitors', label: '价格监控', icon: PriceTag },
  { index: 'commission-configs', label: '佣金配置', icon: Money },
  { index: 'product-tags', label: '商品标签', icon: PriceTag },
  { index: 'product-reviews', label: '商品评价', icon: Star },
  { index: 'sales-targets', label: '销售目标', icon: Trophy },
  { index: 'promo-codes', label: '推广码', icon: Promotion },
  { index: 'content-calendars', label: '内容日历', icon: Calendar },
  { index: 'influencer-collabs', label: '达人合作', icon: UserFilled },
  { index: 'social-medias', label: '社媒管理', icon: ChatDotRound },
  { index: 'email-campaigns', label: '邮件营销', icon: Message },
  { index: 'referral-programs', label: '推荐计划', icon: Share },
  { index: 'loyalty-programs', label: '会员积分', icon: Goods },
  { index: 'events', label: '活动管理', icon: Flag },
  { index: 'seo', label: 'SEO优化', icon: Search },
  { index: 'realtime-analytics', label: '实时分析', icon: TrendCharts },
  { index: 'audience-insights', label: '受众洞察', icon: Avatar },
  { index: 'conversion-funnels', label: '转化漏斗', icon: DataAnalysis },
  { index: 'roi-analysis', label: 'ROI分析', icon: Histogram },
  { index: 'benchmark-reports', label: '基准报告', icon: DataBoard },
  { index: 'custom-dashboards', label: '自定义看板', icon: Monitor },
  { index: 'data-imports', label: '数据导入', icon: Document },
  { index: 'salary', label: '薪资管理', icon: Wallet },
  { index: 'recruitments', label: '招聘管理', icon: User },
  { index: 'onboardings', label: '员工入职', icon: Notebook },
  { index: 'leave-balances', label: '假期余额', icon: Calendar },
  { index: 'team-chat', label: '团队沟通', icon: ChatRound },
  { index: 'okr', label: 'OKR管理', icon: Aim },
  { index: 'budgets', label: '预算管理', icon: Wallet },
  { index: 'profits', label: '利润分析', icon: Money },
  { index: 'invoices', label: '发票管理', icon: Tickets },
  { index: 'payments', label: '收款记录', icon: CreditCard },
  { index: 'insurances', label: '保险记录', icon: Service },
  { index: 'legal-cases', label: '法务案件', icon: Lock },
  { index: 'quality-checks', label: '质量检查', icon: Checked },
  { index: 'workflows', label: '工作流自动化', icon: Setting },
  { index: 'vendor-ratings', label: '供应商评级', icon: Phone },
  { index: 'stock-alerts', label: '库存预警', icon: AlarmClock },
  { index: 'sla', label: 'SLA管理', icon: Shield },
  { index: 'feedbacks', label: '反馈系统', icon: Comment },
  // 企业级功能
  { index: 'system-announcements', label: '系统公告', icon: Notification },
  { index: 'permission-policies', label: '权限策略', icon: Lock },
  { index: 'audit-logs', label: '审计日志', icon: DocumentCopy },
  { index: 'data-backups', label: '数据备份', icon: Upload },
  { index: 'health-monitors', label: '系统监控', icon: Monitor },
  { index: 'integration-configs', label: '集成配置', icon: Position },
  { index: 'workflow-templates', label: '工作流模板', icon: Operation },
  { index: 'notification-templates', label: '通知模板', icon: BellTemplate },
  { index: 'report-schedulers', label: '报表计划', icon: ReportTimer },
  { index: 'export-center', label: '导出中心', icon: Download },
  { index: 'white-label-configs', label: '白标配置', icon: WhiteLabelBrush },
  { index: 'multi-tenant-configs', label: '多租户配置', icon: TenantHouse },
  { index: 'license-management', label: '许可证管理', icon: LicenseKey },
  { index: 'risk-assessments', label: '风险评估', icon: RiskWarning },
  { index: 'disaster-recoveries', label: '灾备管理', icon: DRRecovery },
  { index: 'compliance-audits', label: '合规审计', icon: AuditCheck },
  { index: 'system-configs', label: '系统配置', icon: SysSetting },
  { index: 'feature-flags', label: '功能开关', icon: Open },
  { index: 'api-key-managements', label: 'API密钥', icon: ApiKey },
  { index: 'deployment-records', label: '部署记录', icon: DeployUpload },
]

const navigate = (key) => {
  router.push(`/${key}`)
  if (isMobile.value) drawerVisible.value = false
}

const bottomNavItems = [
  { index: 'dashboard', label: '首页', icon: DataLine },
  { index: 'sessions', label: '直播', icon: VideoCamera },
  { index: 'tasks', label: '任务', icon: Notebook },
  { index: 'notifications', label: '消息', icon: Bell },
  { index: 'more', label: '更多', icon: Grid },
]

let timer = null
let mql = null
const updateTime = () => {
  const d = new Date()
  currentTime.value = d.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  })
}
const onResize = (e) => { isMobile.value = e.matches }

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 3000)
  mql = window.matchMedia('(max-width: 768px)')
  isMobile.value = mql.matches
  mql.addEventListener('change', onResize)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (mql) mql.removeEventListener('change', onResize)
})
</script>

<template>
  <el-container style="height: 100vh">
    <!-- Desktop Sidebar -->
    <el-aside v-if="!isMobile" width="240px" style="background: linear-gradient(180deg, #0d1230 0%, #1a1f4a 100%); position: relative; z-index: 10; display: flex; flex-direction: column; overflow: hidden">
      <div style="padding: 28px 20px 24px; text-align: center; border-bottom: 1px solid var(--border-glow); position: relative;">
        <div style="font-size: 36px; margin-bottom: 4px; filter: drop-shadow(0 0 12px rgba(124, 92, 255, 0.6))">🎬</div>
        <div class="glow-text" style="font-size: 18px; font-weight: 800; letter-spacing: 1px">MCN 管家</div>
        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px; letter-spacing: 2px">LIVE STREAMING OPS</div>
      </div>
      <el-menu :default-active="active" @select="navigate" style="padding: 12px 0; overflow-y: auto; flex: 1">
        <el-menu-item v-for="m in menuItems" :key="m.index" :index="m.index">
          <el-icon style="font-size: 18px"><component :is="m.icon" /></el-icon>
          <span style="margin-left: 4px; font-weight: 500">{{ m.label }}</span>
          <el-tag v-if="m.badge" size="small" style="margin-left: auto; background: var(--grad-4); border: none; color: white; height: 18px; line-height: 18px; padding: 0 6px; font-size: 10px">{{ m.badge }}</el-tag>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Mobile Drawer -->
    <el-drawer v-model="drawerVisible" direction="ltr" :size="280" :with-header="false" :z-index="2000">
      <div style="background: linear-gradient(180deg, #0d1230 0%, #1a1f4a 100%); height: 100%; display: flex; flex-direction: column">
        <div style="padding: 28px 20px 24px; text-align: center; border-bottom: 1px solid var(--border-glow)">
          <div style="font-size: 36px; margin-bottom: 4px; filter: drop-shadow(0 0 12px rgba(124, 92, 255, 0.6))">🎬</div>
          <div class="glow-text" style="font-size: 18px; font-weight: 800; letter-spacing: 1px">MCN 管家</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px; letter-spacing: 2px">LIVE STREAMING OPS</div>
        </div>
        <el-menu :default-active="active" @select="navigate" style="padding: 12px 0; overflow-y: auto; flex: 1">
          <el-menu-item v-for="m in menuItems" :key="m.index" :index="m.index">
            <el-icon style="font-size: 18px"><component :is="m.icon" /></el-icon>
            <span style="margin-left: 4px; font-weight: 500">{{ m.label }}</span>
            <el-tag v-if="m.badge" size="small" style="margin-left: auto; background: var(--grad-4); border: none; color: white; height: 18px; line-height: 18px; padding: 0 6px; font-size: 10px">{{ m.badge }}</el-tag>
          </el-menu-item>
        </el-menu>
      </div>
    </el-drawer>

    <el-container>
      <!-- Header -->
      <el-header style="background: rgba(13, 18, 48, 0.8); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-glow); display: flex; align-items: center; padding: 0 16px; height: 56px; position: relative; z-index: 9">
        <!-- Hamburger (mobile) -->
        <el-icon v-if="isMobile" @click="drawerVisible = true" style="font-size: 24px; color: var(--neon-cyan); cursor: pointer; margin-right: 12px">
          <Fold />
        </el-icon>

        <div style="flex: 1; display: flex; align-items: center; gap: 16px">
          <!-- Mobile: show app name -->
          <span v-if="isMobile" class="glow-text" style="font-size: 16px; font-weight: 800">MCN 管家</span>
          <!-- Desktop: search bar -->
          <div v-else style="padding: 8px 16px; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-glow); border-radius: 12px; display: flex; align-items: center; gap: 8px; min-width: 280px">
            <el-icon style="color: var(--neon-cyan)"><Search /></el-icon>
            <span style="color: var(--text-muted); font-size: 13px">搜索主播、店铺、直播间...</span>
            <span style="margin-left: auto; padding: 2px 6px; background: rgba(0, 229, 255, 0.2); border-radius: 4px; font-size: 10px; color: var(--neon-cyan)">⌘K</span>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 12px">
          <!-- Status indicator -->
          <div class="mobile-hidden" style="display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(0, 255, 157, 0.1); border: 1px solid rgba(0, 255, 157, 0.3); border-radius: 20px">
            <span class="live-dot"></span>
            <span style="font-size: 12px; color: var(--neon-green); font-weight: 600">系统正常</span>
          </div>
          <!-- Clock (desktop only) -->
          <div class="mobile-hidden" style="font-size: 13px; color: var(--text-secondary); font-family: 'Courier New', monospace">{{ currentTime }}</div>
          <!-- Notification -->
          <el-icon style="font-size: 20px; color: var(--text-secondary); cursor: pointer; padding: 8px; border-radius: 8px; background: rgba(255, 255, 255, 0.05)">
            <Bell />
          </el-icon>
          <!-- Avatar -->
          <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--grad-1); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; cursor: pointer; font-size: 13px; box-shadow: 0 4px 12px rgba(124, 92, 255, 0.4)">A</div>
        </div>
      </el-header>

      <!-- Main content -->
      <el-main style="padding: 0; height: calc(100vh - 56px); overflow: hidden">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- Bottom Navigation (mobile only) -->
    <div class="mobile-nav">
      <button v-for="item in bottomNavItems" :key="item.index"
        class="mobile-nav-item"
        :class="{ active: item.index !== 'more' && active === item.index }"
        @click="item.index === 'more' ? (drawerVisible = true) : navigate(item.index)">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </button>
    </div>
  </el-container>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>