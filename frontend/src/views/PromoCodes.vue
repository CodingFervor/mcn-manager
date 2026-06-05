<script setup>
import { ref, onMounted } from 'vue'
import { PromoCodeAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, total_used: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', discount_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      PromoCodeAPI.list(filters.value),
      PromoCodeAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    code: '', discount_type: 'fixed', discount_value: 0, min_order: 0,
    max_uses: 100, used_count: 0, start_date: '', end_date: '', is_active: true
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await PromoCodeAPI.update(form.value.id, form.value)
  else await PromoCodeAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该优惠码？', '提示', { type: 'warning' })
  await PromoCodeAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const discountTypeMap = { fixed: '固定金额', percent: '百分比折扣' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="优惠码管理" subtitle="优惠码生成 · 使用追踪 · 促销管理" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">优惠码总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">激活中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总使用次数</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_used }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索优惠码" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.discount_type" placeholder="优惠类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in discountTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建优惠码</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="code" label="优惠码" width="130">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:700;font-family:monospace">{{ row.code }}</span>
          </template>
        </el-table-column>
        <el-table-column label="优惠类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ discountTypeMap[row.discount_type] || row.discount_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="优惠额度" width="100">
          <template #default="{ row }">
            <span style="color:#ff4757;font-weight:600">
              <template v-if="row.discount_type === 'percent'">{{ row.discount_value }}%</template>
              <template v-else>¥{{ row.discount_value }}</template>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="最低消费" width="90">
          <template #default="{ row }">
            <span>¥{{ row.min_order }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="max_uses" label="最大使用" width="90" />
        <el-table-column prop="used_count" label="已使用" width="80" />
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            <span style="font-size:12px">{{ row.start_date?.slice(0, 10) }} ~ {{ row.end_date?.slice(0, 10) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑优惠码' : '新建优惠码'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优惠码"><el-input v-model="form.code" placeholder="请输入优惠码" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优惠类型">
              <el-select v-model="form.discount_type" style="width:100%">
                <el-option v-for="(v, k) in discountTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="优惠额度"><el-input-number v-model="form.discount_value" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低消费"><el-input-number v-model="form.min_order" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最大使用次数"><el-input-number v-model="form.max_uses" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="form.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.start_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" value-format="YYYY-MM-DD" style="width:100%" />
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
