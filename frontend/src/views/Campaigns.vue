<script setup>
import { ref, onMounted } from 'vue'
import { CampaignAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

const campaigns = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try { campaigns.value = await CampaignAPI.list() } finally { loading.value = false }
}

const activeCount = (s) => campaigns.value.filter(c => c.status === s).length

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="营销活动" subtitle="活动管理 · 促销管理 · 效果追踪" />
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <StatCard label="总活动" :value="campaigns.length" icon="🎪" gradient="g1" />
      <StatCard label="进行中" :value="activeCount('active')" icon="🔥" gradient="g4" />
      <StatCard label="已完成" :value="activeCount('completed')" icon="✅" gradient="g3" />
      <StatCard label="草稿" :value="activeCount('draft')" icon="📝" gradient="g2" />
    </div>
    <div class="glass" style="padding:20px">
      <el-table :data="campaigns" stripe v-loading="loading">
        <el-table-column prop="name" label="活动名称" min-width="200" />
        <el-table-column prop="campaign_type_display" label="类型" width="120" />
        <el-table-column prop="store_name" label="店铺" width="150" />
        <el-table-column prop="target_gmv" label="目标GMV" width="120">
          <template #default="{ row }">¥{{ (row.target_gmv / 10000).toFixed(1) }}万</template>
        </el-table-column>
        <el-table-column prop="actual_gmv" label="实际GMV" width="120">
          <template #default="{ row }">¥{{ (row.actual_gmv / 10000).toFixed(1) }}万</template>
        </el-table-column>
        <el-table-column label="完成率" width="200">
          <template #default="{ row }">
            <el-progress :percentage="Math.min(100, row.completion_rate)" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'draft' ? 'info' : 'warning'" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>
