<script setup>
import { ref, onMounted } from 'vue'
import { CompetitorAPI, FanAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const activeTab = ref('competitor')
const competitors = ref([])
const fanTrend = ref([])
const loading = ref(false)

async function loadCompetitors() {
  loading.value = true
  try { competitors.value = await CompetitorAPI.list() } finally { loading.value = false }
}
async function loadFanTrend() {
  loading.value = true
  try { fanTrend.value = await FanAPI.trend({ days: 30 }) } finally { loading.value = false }
}

const fmtNum = (n) => n >= 10000 ? (n / 10000).toFixed(1) + '万' : n

onMounted(() => { loadCompetitors(); loadFanTrend() })
</script>

<template>
  <div class="page">
    <PageHeader title="竞品与粉丝" subtitle="竞品监控 · 数据追踪 · 粉丝画像分析" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="竞品监控" name="competitor">
        <div class="glass" style="padding:20px">
          <el-table :data="competitors" stripe v-loading="loading">
            <el-table-column prop="name" label="竞品名称" min-width="150" />
            <el-table-column prop="platform" label="平台" width="100">
              <template #default="{ row }"><el-tag size="small">{{ row.platform }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="followers" label="粉丝数" width="120">
              <template #default="{ row }">{{ fmtNum(row.followers) }}</template>
            </el-table-column>
            <el-table-column prop="category" label="领域" width="100" />
            <el-table-column label="数据记录" width="100">
              <template #default="{ row }">{{ row.data?.length || 0 }}条</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="粉丝分析" name="fans">
        <div class="glass" style="padding:20px">
          <el-table :data="fanTrend" stripe v-loading="loading">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="total_fans" label="总粉丝" width="120">
              <template #default="{ row }">{{ fmtNum(row.total_fans) }}</template>
            </el-table-column>
            <el-table-column prop="new_fans" label="新增" width="100">
              <template #default="{ row }"><span style="color:var(--neon-green)">+{{ row.new_fans }}</span></template>
            </el-table-column>
            <el-table-column prop="lost_fans" label="流失" width="100">
              <template #default="{ row }"><span style="color:var(--neon-pink)">-{{ row.lost_fans }}</span></template>
            </el-table-column>
            <el-table-column prop="engagement_rate" label="互动率%" width="100" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
