<script setup>
import { ref, onMounted } from 'vue'
import { CouponAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, active: 0, total_issued: 0, total_used: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', coupon_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      CouponAPI.list(filters.value),
      CouponAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    store: null, name: '', coupon_type: 'fixed', value: 0, min_amount: 0,
    total_count: 100, start_time: '', end_time: '', session: null, status: 'draft'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await CouponAPI.update(form.value.id, form.value)
  else await CouponAPI.create(form.value)
  dialog.value = false
  load()
}

const activateItem = async (row) => {
  await CouponAPI.activate(row.id, {})
  load()
}

const couponTypeMap = { fixed: '满减', percent: '折扣', free_shipping: '包邮', gift: '赠品' }
const statusMap = { draft: '草稿', active: '已激活', paused: '已暂停', expired: '已过期' }
const statusColor = { draft: 'info', active: 'success', paused: 'warning', expired: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="优惠券管理" subtitle="优惠券发放 · 核销统计 · 效果追踪" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">优惠券总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">激活中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已发放</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_issued }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已核销</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.total_used }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索优惠券名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.coupon_type" placeholder="类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in couponTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建优惠券</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="优惠券名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="store_name" label="店铺" width="120" show-overflow-tooltip />
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ couponTypeMap[row.coupon_type] || row.coupon_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面值/折扣" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">
              <template v-if="row.coupon_type === 'percent'">{{ row.value }}%</template>
              <template v-else>¥{{ row.value }}</template>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="门槛" width="90">
          <template #default="{ row }">
            <span>¥{{ row.min_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_count" label="总量" width="70" />
        <el-table-column prop="used_count" label="已用" width="70" />
        <el-table-column prop="remain_count" label="剩余" width="70" />
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            <span style="font-size:12px">{{ row.start_time?.slice(0, 10) }} ~ {{ row.end_time?.slice(0, 10) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'draft' || row.status === 'paused'" size="small" type="success" @click="activateItem(row)">激活</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑优惠券' : '新建优惠券'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优惠券名称"><el-input v-model="form.name" placeholder="请输入名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="form.coupon_type" style="width:100%">
                <el-option v-for="(v, k) in couponTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="面值/折扣"><el-input-number v-model="form.value" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低消费"><el-input-number v-model="form.min_amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发放总量"><el-input-number v-model="form.total_count" :min="1" style="width:100%" /></el-form-item>
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
        <el-form-item label="关联场次ID"><el-input-number v-model="form.session" :min="1" style="width:100%" placeholder="可选" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
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
