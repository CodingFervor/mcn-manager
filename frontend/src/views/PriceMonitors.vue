<script setup>
import { ref, onMounted } from 'vue'
import { PriceMonitorAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, alerts_triggered: 0, avg_price_change: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', platform: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      PriceMonitorAPI.list(filters.value),
      PriceMonitorAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    product_name: '', platform: '', current_price: 0, original_price: 0,
    lowest_price: 0, competitor_price: 0, price_change: 0, alert_triggered: false
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await PriceMonitorAPI.update(form.value.id, form.value)
  else await PriceMonitorAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该监控记录？', '提示', { type: 'warning' })
  await PriceMonitorAPI.update(row.id, row)
  ElMessage.success('删除成功')
  load()
}

const platformMap = { taobao: '淘宝', jd: '京东', pdd: '拼多多', douyin: '抖音', kuaishou: '快手' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="价格监控" subtitle="竞品比价 · 价格波动 · 预警提醒" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">监控商品数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">触发预警</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.alerts_triggered }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均价格变动</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ Number(stats.avg_price_change || 0).toFixed(2) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.platform" placeholder="平台" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建监控</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="商品名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="平台" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ platformMap[row.platform] || row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前价格" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">¥{{ row.current_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="原价" width="90">
          <template #default="{ row }">
            <span>¥{{ row.original_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最低价" width="90">
          <template #default="{ row }">
            <span style="color:#00ff9d;font-weight:600">¥{{ row.lowest_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="竞品价格" width="100">
          <template #default="{ row }">
            <span>¥{{ row.competitor_price }}</span>
          </template>
        </el-table-column>
        <el-table-column label="价格变动" width="100">
          <template #default="{ row }">
            <span :style="{ color: row.price_change > 0 ? '#ff4757' : '#00ff9d', fontWeight: 600 }">
              {{ row.price_change > 0 ? '+' : '' }}{{ row.price_change }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="预警" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.alert_triggered" size="small" type="danger">触发</el-tag>
            <el-tag v-else size="small" type="info">正常</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑监控' : '新建监控'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="请输入商品名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平台">
              <el-select v-model="form.platform" style="width:100%">
                <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="当前价格"><el-input-number v-model="form.current_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="原价"><el-input-number v-model="form.original_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低价"><el-input-number v-model="form.lowest_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="竞品价格"><el-input-number v-model="form.competitor_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="价格变动"><el-input-number v-model="form.price_change" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="触发预警">
              <el-switch v-model="form.alert_triggered" />
            </el-form-item>
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
