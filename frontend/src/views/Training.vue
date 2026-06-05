<script setup>
import { ref, onMounted } from 'vue'
import { TrainingAPI, GoalAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

const activeTab = ref('training')
const courses = ref([])
const goals = ref([])
const goalSummary = ref({})
const loading = ref(false)
const period = ref('2026-06')

async function loadTraining() {
  loading.value = true
  try { courses.value = await TrainingAPI.list() } finally { loading.value = false }
}
async function loadGoals() {
  loading.value = true
  try {
    const res = await GoalAPI.board({ period: period.value })
    goals.value = res.goals || []
    goalSummary.value = res.summary || {}
  } finally { loading.value = false }
}

onMounted(() => { loadTraining(); loadGoals() })
</script>

<template>
  <div class="page">
    <PageHeader title="培训与目标" subtitle="培训课程 · 考核记录 · 目标管理" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="培训管理" name="training">
        <div class="glass" style="padding:20px">
          <el-table :data="courses" stripe v-loading="loading">
            <el-table-column prop="title" label="课程名称" min-width="200" />
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="trainer_name" label="讲师" width="100" />
            <el-table-column prop="duration_minutes" label="时长(分)" width="100" />
            <el-table-column prop="status_display" label="状态" width="100" />
            <el-table-column label="学员数" width="80">
              <template #default="{ row }">{{ row.records?.length || 0 }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="目标管理" name="goals">
        <div class="toolbar">
          <el-input v-model="period" placeholder="周期 如2026-06" style="width:160px" />
          <el-button type="primary" @click="loadGoals">查询</el-button>
        </div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
          <StatCard label="总目标" :value="goalSummary.count || 0" icon="🎯" gradient="g1" />
          <StatCard label="已完成" :value="goalSummary.completed || 0" icon="✅" gradient="g3" />
          <StatCard label="完成率" :value="goalSummary.count ? ((goalSummary.completed / goalSummary.count) * 100).toFixed(1) + '%' : '0%'" icon="📊" gradient="g2" />
        </div>
        <div class="glass" style="padding:20px">
          <el-table :data="goals" stripe v-loading="loading">
            <el-table-column prop="employee_name" label="员工" width="100" />
            <el-table-column prop="metric" label="指标" width="100" />
            <el-table-column prop="target_value" label="目标值" width="120" />
            <el-table-column prop="actual_value" label="实际值" width="120" />
            <el-table-column label="完成率" width="200">
              <template #default="{ row }">
                <el-progress :percentage="Math.min(100, row.completion_rate)" :stroke-width="8" :color="row.completion_rate >= 100 ? '#00ff9d' : row.completion_rate >= 70 ? '#00e5ff' : '#ff4d9e'" />
              </template>
            </el-table-column>
            <el-table-column prop="period_type_display" label="周期" width="80" />
            <el-table-column prop="status_display" label="状态" width="100" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
