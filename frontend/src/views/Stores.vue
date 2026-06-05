<script setup>
import { onMounted, ref, nextTick, onUnmounted } from 'vue'
import echarts from '../echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { StoreAPI, BrandAPI } from '../api'
import { Search, Plus, Shop, Aim, Money, Warning } from '@element-plus/icons-vue'

const list = ref([])
const overview = ref([])
const brands = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({ name: '', platform: 'douyin', brand: null, category: '', status: 'active', monthly_target: 50, store_url: '', remark: '' })
const editingId = ref(null)
const filter = ref({ platform: '', status: '', kw: '' })

const platforms = [['douyin','抖音'],['kuaishou','快手'],['taobao','淘宝'],['xiaohongshu','小红书'],['pdd','拼多多'],['jd','京东']]
const statuses = [['active','运营中'],['paused','已暂停'],['closed','已关停']]
const platformGrad = { douyin: 'g1', kuaishou: 'g3', taobao: 'g5', xiaohongshu: 'g4', pdd: 'g2', jd: 'g6' }

const overviewChart = ref(null)
let chartInst = null

const load = async () => {
  loading.value = true
  try {
    const [s, ov, b] = await Promise.all([
      StoreAPI.list({ platform: filter.value.platform, status: filter.value.status, kw: filter.value.kw }),
      StoreAPI.overview(),
      BrandAPI.list()
    ])
    list.value = s
    overview.value = ov
    brands.value = b
    await nextTick()
    renderChart()
  } finally { loading.value = false }
}

const renderChart = () => {
  if (!overviewChart.value) return
  chartInst = chartInst || echarts.init(overviewChart.value)
  const top = overview.value.slice(0, 12)
  chartInst.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: 'rgba(20,24,56,0.95)', borderColor: '#7c5cff', textStyle: { color: '#fff' } },
    legend: { data: ['GMV(万)', '完成率(%)'], textStyle: { color: '#a8b2d1' }, top: 0 },
    grid: { left: 50, right: 50, top: 40, bottom: 80 },
    xAxis: { type: 'category', data: top.map(s => s.name.slice(0, 12) + (s.name.length > 12 ? '..' : '')), axisLine: { lineStyle: { color: '#3a3f5f' } }, axisLabel: { color: '#a8b2d1', rotate: 30, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'GMV(万)', nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { lineStyle: { color: 'rgba(124,92,255,0.1)' } }, axisLabel: { color: '#a8b2d1' } },
      { type: 'value', name: '完成率(%)', max: 150, nameTextStyle: { color: '#a8b2d1' }, axisLine: { lineStyle: { color: '#3a3f5f' } }, splitLine: { show: false }, axisLabel: { color: '#a8b2d1' } }
    ],
    series: [
      { name: 'GMV(万)', type: 'bar', data: top.map(s => +(s.monthly_gmv/10000).toFixed(1)),
        itemStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#7c5cff' }, { offset: 1, color: 'rgba(124,92,255,0.2)' }]), borderRadius: [8, 8, 0, 0] }
      },
      { name: '完成率(%)', type: 'line', yAxisIndex: 1, smooth: true, symbolSize: 8,
        data: top.map(s => s.target_rate), itemStyle: { color: '#ff4d9e' },
        lineStyle: { color: '#ff4d9e', width: 3 }
      }
    ]
  })
}

const onResize = () => chartInst?.resize()
window.addEventListener('resize', onResize)
onUnmounted(() => { window.removeEventListener('resize', onResize); chartInst?.dispose() })

const openCreate = () => {
  editingId.value = null
  form.value = { name: '', platform: 'douyin', brand: null, category: '', status: 'active', monthly_target: 50, store_url: '', remark: '' }
  dialogVisible.value = true
}
const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}
const submit = async () => {
  if (editingId.value) await StoreAPI.update(editingId.value, form.value)
  else await StoreAPI.create(form.value)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}
const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除店铺「${row.name}」？`, '提示', { type: 'warning' })
  await StoreAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">店铺管理</h1>
    <div class="page-subtitle">管理所有直播电商代运营店铺 · 追踪 GMV 表现</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><Shop /></el-icon>
          <div class="stat-label">运营中店铺</div>
          <div class="stat-value">{{ list.filter(s => s.status === 'active').length }}</div>
          <div class="stat-trend">⚡ 实时监控</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><Money /></el-icon>
          <div class="stat-label">总 GMV (30天)</div>
          <div class="stat-value">¥{{ (overview.reduce((s, o) => s + o.monthly_gmv, 0) / 10000).toFixed(0) }}万</div>
          <div class="stat-trend">📈 持续增长</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g2"><el-icon class="stat-icon"><Aim /></el-icon>
          <div class="stat-label">品牌合作</div>
          <div class="stat-value">{{ brands.length }}</div>
          <div class="stat-trend">🤝 战略合作</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><Warning /></el-icon>
          <div class="stat-label">已暂停</div>
          <div class="stat-value">{{ list.filter(s => s.status === 'paused').length }}</div>
          <div class="stat-trend">⚠️ 待跟进</div>
        </div>
      </el-col>
    </el-row>

    <el-card style="margin-bottom: 16px">
      <template #header>
        <div style="display: flex; align-items: center; gap: 8px">
          <span style="font-size: 16px">📊</span>
          <span>店铺 GMV 排行 TOP 12（近30天）</span>
        </div>
      </template>
      <div ref="overviewChart" style="height: 320px"></div>
    </el-card>

    <el-card>
      <div class="toolbar">
        <div style="position: relative; flex: 1; max-width: 300px">
          <el-icon style="position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); z-index: 1"><Search /></el-icon>
          <el-input v-model="filter.kw" placeholder="搜索店铺名" clearable @keyup.enter="load" style="--el-input-padding-left: 36px" />
        </div>
        <el-select v-model="filter.platform" placeholder="🎯 平台" clearable style="width: 140px" @change="load">
          <el-option v-for="p in platforms" :key="p[0]" :label="p[1]" :value="p[0]" />
        </el-select>
        <el-select v-model="filter.status" placeholder="📡 状态" clearable style="width: 140px" @change="load">
          <el-option v-for="s in statuses" :key="s[0]" :label="s[1]" :value="s[0]" />
        </el-select>
        <el-button @click="load">查询</el-button>
        <div style="flex: 1"></div>
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon><span style="margin-left: 4px">新增店铺</span></el-button>
      </div>

      <el-table :data="list" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="店铺" min-width="220">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; gap: 12px">
              <div :class="`stat-card ${platformGrad[row.platform] || 'g2'}`" style="width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: 700; padding: 0; flex-shrink: 0">
                {{ row.platform_display[0] }}
              </div>
              <div>
                <div style="font-weight: 600; color: white">{{ row.name }}</div>
                <div style="font-size: 11px; color: var(--text-muted)">{{ row.brand_name || '无品牌' }} · {{ row.category }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="平台" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ row.platform_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'active' ? 'success' : row.status === 'paused' ? 'warning' : 'info'">
              <span class="status-dot" :class="row.status === 'active' ? 'status-online' : 'status-busy'"></span>
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="月度目标" width="110">
          <template #default="{ row }">¥{{ row.monthly_target }}万</template>
        </el-table-column>
        <el-table-column label="30天GMV" width="140">
          <template #default="{ row }">
            <span style="color: var(--neon-pink); font-weight: 700; font-size: 15px">¥{{ (row.monthly_gmv/10000).toFixed(1) }}万</span>
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="180">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(Math.round(row.target_rate), 100)" :status="row.target_rate >= 100 ? 'success' : row.target_rate < 50 ? 'exception' : ''" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="openEdit(row)" style="color: var(--neon-cyan)">编辑</el-button>
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑店铺' : '新增店铺'" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="店铺名"><el-input v-model="form.name" placeholder="如：完美日记抖音旗舰店" /></el-form-item>
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width: 100%">
            <el-option v-for="p in platforms" :key="p[0]" :label="p[1]" :value="p[0]" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌方">
          <el-select v-model="form.brand" placeholder="选择品牌" style="width: 100%" filterable clearable>
            <el-option v-for="b in brands" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类目"><el-input v-model="form.category" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="s in statuses" :key="s[0]" :label="s[1]" :value="s[0]" />
          </el-select>
        </el-form-item>
        <el-form-item label="月度目标"><el-input-number v-model="form.monthly_target" :min="0" :max="10000" /></el-form-item>
        <el-form-item label="店铺链接"><el-input v-model="form.store_url" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
