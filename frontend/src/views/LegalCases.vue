<script setup>
import { ref, onMounted } from 'vue'
import { LegalCaseAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_case_type: {}, by_status: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', case_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      LegalCaseAPI.list(filters.value),
      LegalCaseAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    title: '', case_type: '', parties: '', status: 'filed',
    filed_date: '', hearing_date: '', lawyer: ''
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) {
      await LegalCaseAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await LegalCaseAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该法律案件?', '提示', { type: 'warning' }).then(async () => {
    await LegalCaseAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const caseTypeMap = { contract: '合同纠纷', ip: '知识产权', labor: '劳动争议', tort: '侵权责任', other: '其他' }
const statusMap = { filed: '已立案', hearing: '审理中', settled: '已和解', closed: '已结案' }
const statusColor = { filed: 'info', hearing: 'warning', settled: 'success', closed: '' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="法律案件" subtitle="案件管理 · 诉讼追踪 · 法律顾问" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">案件总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">审理中</div>
        <div class="stat-value">{{ stats.by_status?.hearing || 0 }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已结案</div>
        <div class="stat-value">{{ stats.by_status?.closed || 0 }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">案件类型</div>
        <div class="stat-value">{{ Object.keys(stats.by_case_type || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索案件标题/当事人" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.case_type" placeholder="案件类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in caseTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建案件</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="案件标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="案件类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ caseTypeMap[row.case_type] || row.case_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parties" label="当事人" width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="filed_date" label="立案日期" width="110" />
        <el-table-column prop="hearing_date" label="开庭日期" width="110" />
        <el-table-column prop="lawyer" label="律师" width="100" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑案件' : '新建案件'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="案件标题"><el-input v-model="form.title" placeholder="请输入案件标题" /></el-form-item>
        <el-form-item label="案件类型">
          <el-select v-model="form.case_type" style="width: 100%">
            <el-option v-for="(v, k) in caseTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="当事人"><el-input v-model="form.parties" placeholder="当事人信息，多个用逗号分隔" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="立案日期">
              <el-date-picker v-model="form.filed_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开庭日期">
              <el-date-picker v-model="form.hearing_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="律师"><el-input v-model="form.lawyer" placeholder="代理律师" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
