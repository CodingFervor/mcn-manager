<script setup>
import { ref, onMounted } from 'vue'
import { KOLAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

const kols = ref([])
const loading = ref(false)
const filters = ref({ status: '', kw: '' })

async function load() {
  loading.value = true
  try { kols.value = await KOLAPI.list(filters.value) } finally { loading.value = false }
}

const fmtNum = (n) => n >= 10000 ? (n / 10000).toFixed(1) + '万' : n
const statusColor = { contacting: 'info', negotiating: 'warning', cooperating: 'success', completed: '' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="达人对接" subtitle="KOL资源管理 · 合作跟进 · 费用评估" />
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <StatCard label="总达人" :value="kols.length" icon="🌟" gradient="g1" />
      <StatCard label="合作中" :value="kols.filter(k => k.status === 'cooperating').length" icon="🤝" gradient="g3" />
      <StatCard label="接洽中" :value="kols.filter(k => k.status === 'contacting').length" icon="💬" gradient="g2" />
    </div>
    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索达人/领域" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option label="接洽中" value="contacting" /><el-option label="谈判中" value="negotiating" />
        <el-option label="合作中" value="cooperating" /><el-option label="已结束" value="completed" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
    </div>
    <div class="glass" style="padding:20px">
      <el-table :data="kols" stripe v-loading="loading">
        <el-table-column prop="name" label="达人名称" min-width="150" />
        <el-table-column prop="platform_display" label="平台" width="100" />
        <el-table-column prop="followers" label="粉丝数" width="120">
          <template #default="{ row }">{{ fmtNum(row.followers) }}</template>
        </el-table-column>
        <el-table-column prop="category" label="领域" width="100" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="fee_estimate" label="预估费用" width="120">
          <template #default="{ row }">¥{{ row.fee_estimate }}</template>
        </el-table-column>
        <el-table-column prop="our_contact_name" label="我方对接" width="100" />
        <el-table-column prop="status_display" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>
