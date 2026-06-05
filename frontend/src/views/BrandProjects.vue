<script setup>
import { ref, onMounted } from 'vue'
import { BrandProjectAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, executing: 0, total_budget: 0, total_revenue: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', priority: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      BrandProjectAPI.list(filters.value),
      BrandProjectAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', brand: '', contact_person: '', contact_phone: '', status: 'negotiating',
    priority: 'medium', pm: null, total_budget: 0, target_gmv: 0,
    start_date: '', end_date: '', requirements: '', deliverables: '', notes: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await BrandProjectAPI.update(form.value.id, form.value)
  else await BrandProjectAPI.create(form.value)
  dialog.value = false
  load()
}

const statusMap = { negotiating: '洽谈中', confirmed: '已确认', executing: '执行中', delivered: '已交付', completed: '已完成', cancelled: '已取消' }
const statusColor = { negotiating: 'info', confirmed: 'primary', executing: 'warning', delivered: 'success', completed: 'success', cancelled: 'danger' }
const priorityMap = { low: '低', medium: '中', high: '高', urgent: '紧急' }
const priorityColor = { low: 'info', medium: '', high: 'warning', urgent: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="品牌合作" subtitle="品牌对接 · 项目管理 · 交付追踪" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">项目总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">执行中</div>
        <div class="stat-value">{{ stats.executing }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总预算</div>
        <div class="stat-value">¥{{ Number(stats.total_budget || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总营收</div>
        <div class="stat-value">¥{{ Number(stats.total_revenue || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索项目/品牌" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="优先级" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in priorityMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建项目</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="项目名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="brand" label="品牌方" width="120" />
        <el-table-column prop="contact_person" label="对接人" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="priorityColor[row.priority]" effect="dark">{{ priorityMap[row.priority] || row.priority_display || row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pm_name" label="项目经理" width="100" />
        <el-table-column prop="anchor_names" label="参与主播" width="120" show-overflow-tooltip />
        <el-table-column label="总预算" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.total_budget).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实际营收" width="110">
          <template #default="{ row }">
            <span style="color: var(--neon-green); font-weight: 600">¥{{ Number(row.actual_revenue || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="目标GMV" width="110">
          <template #default="{ row }">
            <span>¥{{ Number(row.target_gmv).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="周期" width="180">
          <template #default="{ row }">
            <span>{{ row.start_date }} ~ {{ row.end_date }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑项目' : '新建项目'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="项目名称"><el-input v-model="form.name" placeholder="请输入项目名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌方"><el-input v-model="form.brand" placeholder="品牌方名称" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="对接人"><el-input v-model="form.contact_person" placeholder="对接人姓名" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话"><el-input v-model="form.contact_phone" placeholder="联系电话" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="(v, k) in priorityMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="项目经理ID"><el-input-number v-model="form.pm" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总预算"><el-input-number v-model="form.total_budget" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="目标GMV"><el-input-number v-model="form.target_gmv" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="需求说明"><el-input v-model="form.requirements" type="textarea" :rows="3" placeholder="项目需求" /></el-form-item>
        <el-form-item label="交付物"><el-input v-model="form.deliverables" type="textarea" :rows="3" placeholder="交付物清单" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" placeholder="备注信息" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
