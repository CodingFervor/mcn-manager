<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RecruitmentAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, open_count: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', status: '', department: '' })

const statusMap = { open: '招聘中', interviewing: '面试中', offered: '已发Offer', filled: '已到岗', closed: '已关闭' }
const statusColor = { open: 'success', interviewing: 'primary', offered: 'warning', filled: 'info', closed: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      RecruitmentAPI.list(filters.value),
      RecruitmentAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { position: '', department: '', candidates_count: 0, status: 'open', deadline: '', salary_range: '', requirements: '' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await RecruitmentAPI.update(editingId.value, form.value)
  else await RecruitmentAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除招聘「${row.position}」？`, '提示', { type: 'warning' })
  await RecruitmentAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="招聘管理" subtitle="岗位发布 · 候选人跟踪 · 招聘流程" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">招聘岗位数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">各状态分布</div>
        <div class="stat-value" style="font-size: 13px; line-height: 1.6">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin-right: 8px">{{ statusMap[k] || k }}: {{ v }}</span>
        </div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">开放中岗位</div>
        <div class="stat-value">{{ stats.open_count }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索岗位/部门" style="width: 200px" @keyup.enter="load" />
      <el-input v-model="filters.department" placeholder="部门" style="width: 130px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 发布岗位</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="position" label="招聘岗位" min-width="140" show-overflow-tooltip fixed />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="candidates_count" label="候选人数" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">{{ row.candidates_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deadline" label="截止日期" width="120" />
        <el-table-column prop="salary_range" label="薪资范围" width="140" />
        <el-table-column prop="requirements" label="要求" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑岗位' : '发布岗位'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="招聘岗位"><el-input v-model="form.position" placeholder="请输入岗位名称" /></el-form-item>
        <el-form-item label="部门"><el-input v-model="form.department" placeholder="请输入所属部门" /></el-form-item>
        <el-form-item label="候选人数"><el-input-number v-model="form.candidates_count" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期"><el-date-picker v-model="form.deadline" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="薪资范围"><el-input v-model="form.salary_range" placeholder="如: 8K-15K" /></el-form-item>
        <el-form-item label="岗位要求"><el-input v-model="form.requirements" type="textarea" :rows="4" placeholder="请输入岗位要求" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
