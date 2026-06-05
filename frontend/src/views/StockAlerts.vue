<script setup>
import { ref, onMounted } from 'vue'
import { StockAlertAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, by_alert_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', alert_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      StockAlertAPI.list(filters.value),
      StockAlertAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    product_name: '', warehouse: '', current_stock: 0,
    threshold: 0, alert_type: '', status: 'active'
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
      await StockAlertAPI.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await StockAlertAPI.create(form.value)
      ElMessage.success('创建成功')
    }
    dialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

const removeItem = (row) => {
  ElMessageBox.confirm('确认删除该库存预警?', '提示', { type: 'warning' }).then(async () => {
    await StockAlertAPI.remove(row.id)
    ElMessage.success('删除成功')
    load()
  }).catch(() => {})
}

const resolveItem = async (row) => {
  try {
    await StockAlertAPI.update(row.id, { status: 'resolved' })
    ElMessage.success('已标记为已解决')
    load()
  } catch { ElMessage.error('操作失败') }
}

const alertTypeMap = { low: '库存不足', overstock: '库存积压', expiry: '即将过期', damaged: '损坏预警' }
const statusMap = { active: '活跃', resolved: '已解决', ignored: '已忽略' }
const statusColor = { active: 'danger', resolved: 'success', ignored: 'info' }
const alertTypeIcon = { low: 'warning', overstock: 'info', expiry: 'warning', damaged: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="库存预警" subtitle="库存监控 · 预警管理 · 补货提醒" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">预警总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">活跃预警</div>
        <div class="stat-value" style="color: #ff4d9e">{{ stats.active }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">库存不足</div>
        <div class="stat-value">{{ stats.by_alert_type?.low || 0 }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">已解决</div>
        <div class="stat-value">{{ list.filter(i => i.status === 'resolved').length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品/仓库" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.alert_type" placeholder="预警类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in alertTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建预警</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="商品名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="warehouse" label="仓库" width="120" />
        <el-table-column label="当前库存" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.current_stock <= row.threshold ? '#ff4d9e' : 'var(--neon-cyan)', fontWeight: 600 }">
              {{ row.current_stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="预警阈值" width="100" />
        <el-table-column label="预警类型" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="alertTypeIcon[row.alert_type]">{{ alertTypeMap[row.alert_type] || row.alert_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'active'" size="small" type="success" @click="resolveItem(row)">解决</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑预警' : '新建预警'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="商品名称" /></el-form-item>
        <el-form-item label="仓库"><el-input v-model="form.warehouse" placeholder="仓库名称" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="当前库存"><el-input-number v-model="form.current_stock" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预警阈值"><el-input-number v-model="form.threshold" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="预警类型">
          <el-select v-model="form.alert_type" style="width: 100%">
            <el-option v-for="(v, k) in alertTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
