<script setup>
import { ref, onMounted } from 'vue'
import { SupplierAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const suppliers = ref([])
const stats = ref({ total: 0, active: 0, avg_rating: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

const categoryMap = {
  product: '产品供应', equipment: '设备供应',
  service: '服务合作', logistics: '物流合作', other: '其他'
}
const statusColor = { active: 'success', paused: 'warning', terminated: 'danger' }
const statusLabel = { active: '合作中', paused: '已暂停', terminated: '已终止' }

async function loadStats() {
  try { stats.value = await SupplierAPI.stats() } catch { stats.value = { total: 0, active: 0, avg_rating: 0 } }
}

async function load() {
  loading.value = true
  try { suppliers.value = await SupplierAPI.list(filters.value) }
  finally { loading.value = false }
}

const openCreate = () => {
  form.value = { category: 'product', status: 'active', rating: 3 }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  if (form.value.id) await SupplierAPI.update(form.value.id, form.value)
  else await SupplierAPI.create(form.value)
  dialog.value = false
  load()
  loadStats()
}

const remove = async (id) => { await SupplierAPI.remove(id); load(); loadStats() }

onMounted(() => { load(); loadStats() })
</script>

<template>
  <div class="page">
    <PageHeader title="供应商管理" subtitle="供应商库 · 合作管理 · 评级追踪" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-icon">🏢</div>
        <div class="stat-label">供应商总数</div>
        <div class="stat-value">{{ stats.total || 0 }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-icon">✅</div>
        <div class="stat-label">合作中</div>
        <div class="stat-value">{{ stats.active || 0 }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-icon">⭐</div>
        <div class="stat-label">平均评级</div>
        <div class="stat-value">{{ Number(stats.avg_rating || 0).toFixed(1) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索供应商名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="合作状态" clearable @change="load" style="width:130px">
        <el-option label="合作中" value="active" />
        <el-option label="已暂停" value="paused" />
        <el-option label="已终止" value="terminated" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 添加供应商</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="suppliers" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="供应商名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column label="供应类别" width="110">
          <template #default="{ row }">{{ categoryMap[row.category] || row.category }}</template>
        </el-table-column>
        <el-table-column label="合作状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusLabel[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="评级" width="160">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled :colors="['#ff4d9e','#ffd23f','#00ff9d']" />
          </template>
        </el-table-column>
        <el-table-column prop="main_products" label="主营产品" width="150" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="供应商" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="供应商名称"><el-input v-model="form.name" placeholder="请输入供应商名称" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="联系人"><el-input v-model="form.contact_person" placeholder="联系人姓名" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话"><el-input v-model="form.phone" placeholder="联系电话" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="邮箱"><el-input v-model="form.email" placeholder="邮箱地址" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" type="textarea" :rows="2" placeholder="详细地址" /></el-form-item>
        <el-form-item label="供应类别">
          <el-select v-model="form.category" style="width:100%">
            <el-option label="产品供应" value="product" />
            <el-option label="设备供应" value="equipment" />
            <el-option label="服务合作" value="service" />
            <el-option label="物流合作" value="logistics" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="合作状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="合作中" value="active" />
            <el-option label="已暂停" value="paused" />
            <el-option label="已终止" value="terminated" />
          </el-select>
        </el-form-item>
        <el-form-item label="评级">
          <el-rate v-model="form.rating" :colors="['#ff4d9e','#ffd23f','#00ff9d']" show-text />
        </el-form-item>
        <el-form-item label="主营产品"><el-input v-model="form.main_products" placeholder="主营产品，逗号分隔" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" placeholder="备注信息" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
