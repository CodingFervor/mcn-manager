<script setup>
import { ref, onMounted } from 'vue'
import { SalesTargetAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, target_amount: 0, actual_amount: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', target_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SalesTargetAPI.list(filters.value),
      SalesTargetAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', target_type: 'anchor', period: '', target_amount: 0,
    actual_amount: 0, completion_rate: 0, status: 'active'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await SalesTargetAPI.update(form.value.id, form.value)
  else await SalesTargetAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const targetTypeMap = { anchor: '主播', store: '店铺', team: '团队', category: '品类' }
const statusMap = { active: '进行中', completed: '已完成', failed: '未达成' }
const statusColor = { active: 'success', completed: 'info', failed: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="销售目标" subtitle="目标设定 · 进度跟踪 · 达成分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">目标总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">目标金额</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">¥{{ Number(stats.target_amount || 0).toLocaleString() }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已完成金额</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">¥{{ Number(stats.actual_amount || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索目标名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.target_type" placeholder="目标类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in targetTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建目标</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="目标名称" min-width="130" show-overflow-tooltip />
        <el-table-column label="目标类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ targetTypeMap[row.target_type] || row.target_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="周期" width="100" />
        <el-table-column label="目标金额" width="110">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">¥{{ Number(row.target_amount || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实际金额" width="110">
          <template #default="{ row }">
            <span style="color:#ffd23f;font-weight:600">¥{{ Number(row.actual_amount || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="完成率" width="130">
          <template #default="{ row }">
            <el-progress :percentage="Number(row.completion_rate || 0)" :stroke-width="10" :color="row.completion_rate >= 100 ? '#00ff9d' : '#00e5ff'" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑销售目标' : '新建销售目标'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标名称"><el-input v-model="form.name" placeholder="请输入目标名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标类型">
              <el-select v-model="form.target_type" style="width:100%">
                <el-option v-for="(v, k) in targetTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标金额"><el-input-number v-model="form.target_amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际金额"><el-input-number v-model="form.actual_amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="完成率(%)"><el-input-number v-model="form.completion_rate" :min="0" :max="999" :precision="1" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
