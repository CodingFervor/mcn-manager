<script setup>
import { ref, onMounted } from 'vue'
import { InventoryAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_quantity: 0, total_locked: 0, low_stock_count: 0 })
const loading = ref(false)
const dialog = ref(false)
const restockDialog = ref(false)
const form = ref({})
const restockForm = ref({})
const filters = ref({ kw: '', warehouse: '', low_stock: false })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      InventoryAPI.list(filters.value),
      InventoryAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    product: null, warehouse: '', sku: '', quantity: 0,
    safety_stock: 0, locked_quantity: 0, cost_price: 0,
    supplier: null, location: ''
  }
  dialog.value = true
}

async function save() {
  if (form.value.id) {
    await InventoryAPI.update(form.value.id, form.value)
  } else {
    await InventoryAPI.create(form.value)
  }
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await InventoryAPI.remove(row.id)
  load()
}

const openRestock = (row) => {
  restockForm.value = { id: row.id, quantity: 0 }
  restockDialog.value = true
}

async function submitRestock() {
  await InventoryAPI.restock(restockForm.value.id, { quantity: restockForm.value.quantity })
  restockDialog.value = false
  load()
}

const loadLowStock = async () => {
  loading.value = true
  try {
    const data = await InventoryAPI.lowStock()
    list.value = data
  } finally { loading.value = false }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="库存管理" subtitle="多仓库存 · 安全预警 · 补货管理" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">SKU总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总库存量</div>
        <div class="stat-value">{{ Number(stats.total_quantity || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">锁定库存</div>
        <div class="stat-value">{{ Number(stats.total_locked || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">低库存预警</div>
        <div class="stat-value">{{ stats.low_stock_count }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索SKU/商品/仓库" style="width: 200px" @keyup.enter="load" />
      <el-input v-model="filters.warehouse" placeholder="仓库" style="width: 140px" @keyup.enter="load" />
      <el-checkbox v-model="filters.low_stock" @change="filters.low_stock ? loadLowStock() : load()" style="color: var(--text-primary)">仅低库存</el-checkbox>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建库存</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="商品" min-width="140" show-overflow-tooltip />
        <el-table-column prop="warehouse" label="仓库" width="100" />
        <el-table-column prop="sku" label="SKU" width="140" />
        <el-table-column label="库存量" width="90">
          <template #default="{ row }">
            <span :style="{ color: row.quantity <= row.safety_stock ? '#ff4757' : 'var(--neon-green)', fontWeight: 600 }">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="90" />
        <el-table-column prop="locked_quantity" label="锁定" width="80" />
        <el-table-column label="成本价" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.cost_price).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="supplier_name" label="供应商" width="100" />
        <el-table-column prop="location" label="库位" width="100" />
        <el-table-column prop="last_restock" label="最近补货" width="170" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="warning" @click="openRestock(row)">补货</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建库存" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width: 100%" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="仓库"><el-input v-model="form.warehouse" placeholder="仓库名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU"><el-input v-model="form.sku" placeholder="SKU编码" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="库存量"><el-input-number v-model="form.quantity" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="安全库存"><el-input-number v-model="form.safety_stock" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="锁定量"><el-input-number v-model="form.locked_quantity" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="成本价"><el-input-number v-model="form.cost_price" :min="0" :precision="2" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商ID"><el-input-number v-model="form.supplier" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="库位"><el-input v-model="form.location" placeholder="库位编码" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="restockDialog" title="补货" width="400px">
      <el-form :model="restockForm" label-width="80px">
        <el-form-item label="补货数量">
          <el-input-number v-model="restockForm.quantity" :min="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="restockDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRestock">确认补货</el-button>
      </template>
    </el-dialog>
  </div>
</template>
