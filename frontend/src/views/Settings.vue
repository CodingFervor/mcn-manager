<script setup>
import { ref, onMounted } from 'vue'
import { ExportAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const exports = ref([])
const loading = ref(false)
const activeTab = ref('export')
const exportType = ref('sessions')

async function loadExports() {
  loading.value = true
  try { exports.value = await ExportAPI.list() } finally { loading.value = false }
}
const doExport = async () => {
  loading.value = true
  try {
    const res = await ExportAPI.create({ export_type: exportType.value, params: {} })
    // 下载 CSV
    if (res.csv_content) {
      const blob = new Blob(['\uFEFF' + res.csv_content], { type: 'text/csv;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `${exportType.value}_${new Date().toISOString().slice(0,10)}.csv`; a.click()
      URL.revokeObjectURL(url)
    }
    loadExports()
  } finally { loading.value = false }
}

onMounted(loadExports)
</script>

<template>
  <div class="page">
    <PageHeader title="系统工具" subtitle="数据导出 · 操作日志 · 系统设置" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="数据导出" name="export">
        <div class="toolbar">
          <el-select v-model="exportType" style="width:200px">
            <el-option label="直播数据" value="sessions" />
            <el-option label="考勤数据" value="attendance" />
            <el-option label="财务数据" value="finance" />
          </el-select>
          <el-button type="primary" @click="doExport" :loading="loading">📥 导出 CSV</el-button>
        </div>
        <div class="glass" style="padding:20px">
          <el-table :data="exports" stripe>
            <el-table-column prop="name" label="导出名称" min-width="200" />
            <el-table-column prop="export_type" label="类型" width="120" />
            <el-table-column prop="row_count" label="行数" width="100" />
            <el-table-column prop="file_size" label="大小" width="100">
              <template #default="{ row }">{{ (row.file_size / 1024).toFixed(1) }}KB</template>
            </el-table-column>
            <el-table-column prop="status_display" label="状态" width="100" />
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">{{ row.created_at?.slice(0, 19) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="操作日志" name="logs">
        <div class="glass" style="padding:20px">
          <el-table :data="exports" stripe>
            <el-table-column prop="name" label="操作" min-width="200" />
            <el-table-column prop="creator" label="操作人" width="120" />
            <el-table-column prop="created_at" label="时间" width="180" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
