<script setup>
import { ref, onMounted } from 'vue'
import { FlashSaleAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, ongoing: 0, total_sold: 0, total_revenue: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      FlashSaleAPI.list(filters.value),
      FlashSaleAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    product: null, session: null, original_price: 0, sale_price: 0,
    total_stock: 100, start_time: '', end_time: '', limit_per_user: 1,
    status: 'pending', priority: 0
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await FlashSaleAPI.update(form.value.id, form.value)
  else await FlashSaleAPI.create(form.value)
  dialog.value = false
  load()
}

const statusMap = { pending: '待开始', ongoing: '进行中', ended: '已结束', cancelled: '已取消' }
const statusColor = { pending: 'info', ongoing: 'success', ended: 'warning', cancelled: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="秒杀活动" subtitle="限时抢购 · 库存管理 · 活动排期" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活动总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">进行中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.ongoing }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已售数量</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_sold }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总销售额</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">¥{{ Number(stats.total_revenue || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品/活动" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建秒杀</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="商品" min-width="150" show-overflow-tooltip />
        <el-table-column prop="session_title" label="直播场次" width="150" show-overflow-tooltip />
        <el-table-column label="原价" width="90">
          <template #default="{ row }">
            <span>¥{{ row.original_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="秒杀价" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">¥{{ row.sale_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_stock" label="总库存" width="80" />
        <el-table-column prop="sold_count" label="已售" width="80" />
        <el-table-column label="销量进度" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.total_stock ? Math.round(row.sold_count / row.total_stock * 100) : 0" :stroke-width="10" />
          </template>
        </el-table-column>
        <el-table-column prop="limit_per_user" label="限购" width="70" />
        <el-table-column label="活动时间" width="180">
          <template #default="{ row }">
            <span style="font-size:12px">{{ row.start_time?.slice(0, 16) }}<br/>{{ row.end_time?.slice(0, 16) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="70" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑秒杀' : '新建秒杀'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场次ID"><el-input-number v-model="form.session" :min="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="原价"><el-input-number v-model="form.original_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="秒杀价"><el-input-number v-model="form.sale_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="总库存"><el-input-number v-model="form.total_stock" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每人限购"><el-input-number v-model="form.limit_per_user" :min="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级"><el-input-number v-model="form.priority" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
