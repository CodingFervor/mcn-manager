<script setup>
import { ref, onMounted } from 'vue'
import { AssetAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, available: 0, in_use: 0, total_value: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', status: '', category: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      AssetAPI.list(filters.value),
      AssetAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { name: '', category: '', brand_model: '', serial_number: '', status: 'available', purchase_price: 0, purchase_date: '', notes: '' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await AssetAPI.update(editingId.value, form.value)
  else await AssetAPI.create(form.value)
  dialog.value = false
  load()
}

const remove = async (id) => { await AssetAPI.remove(id); load() }

const categoryMap = { camera: '摄像机', light: '灯光', phone: '手机', mic: '麦克风', computer: '电脑', prop: '道具', display: '显示器', other: '其他' }
const assetStatusMap = { available: '空闲', in_use: '使用中', maintenance: '维修中', retired: '已报废' }
const assetStatusColor = { available: 'success', in_use: 'primary', maintenance: 'warning', retired: 'info' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="设备资产" subtitle="设备管理 · 资产追踪 · 维护记录" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">设备总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">空闲可用</div>
        <div class="stat-value">{{ stats.available }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">使用中</div>
        <div class="stat-value">{{ stats.in_use }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">资产总值</div>
        <div class="stat-value">¥{{ Number(stats.total_value || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索设备名/序列号" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.category" placeholder="类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in assetStatusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 添加设备</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="设备名称" min-width="140" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ categoryMap[row.category] || row.category }}</template>
        </el-table-column>
        <el-table-column prop="brand_model" label="品牌型号" width="150" />
        <el-table-column prop="serial_number" label="序列号" width="140" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="assetStatusColor[row.status]">{{ assetStatusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assigned_to_name" label="使用人" width="100" />
        <el-table-column prop="room_name" label="所在直播间" width="130" />
        <el-table-column label="购入价格" width="110">
          <template #default="{ row }">¥{{ row.purchase_price }}</template>
        </el-table-column>
        <el-table-column prop="purchase_date" label="购入日期" width="120" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑设备' : '添加设备'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="设备名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="品牌型号"><el-input v-model="form.brand_model" /></el-form-item>
        <el-form-item label="序列号"><el-input v-model="form.serial_number" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in assetStatusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="购入价格"><el-input-number v-model="form.purchase_price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="购入日期"><el-date-picker v-model="form.purchase_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
