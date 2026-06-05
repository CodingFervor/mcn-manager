<script setup>
import { ref, onMounted } from 'vue'
import { CommissionConfigAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, avg_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', category: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      CommissionConfigAPI.list(filters.value),
      CommissionConfigAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', category: '', rate: 0, min_amount: 0, max_amount: 0,
    anchor_rate: 0, platform_rate: 0, is_active: true
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await CommissionConfigAPI.update(form.value.id, form.value)
  else await CommissionConfigAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该佣金配置？', '提示', { type: 'warning' })
  await CommissionConfigAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const categoryMap = { beauty: '美妆', fashion: '服饰', food: '食品', electronics: '数码', home: '家居',母婴: '母婴' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="佣金配置" subtitle="佣金规则 · 费率管理 · 分佣设置" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">配置总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均费率</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ Number(stats.avg_rate || 0).toFixed(2) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索配置名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.category" placeholder="分类" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建配置</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="配置名称" min-width="130" show-overflow-tooltip />
        <el-table-column label="分类" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ categoryMap[row.category] || row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="佣金费率" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">{{ row.rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="最低金额" width="100">
          <template #default="{ row }">
            <span>¥{{ row.min_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="最高金额" width="100">
          <template #default="{ row }">
            <span>¥{{ row.max_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="主播分成" width="90">
          <template #default="{ row }">
            <span style="color:#ffd23f;font-weight:600">{{ row.anchor_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="平台分成" width="90">
          <template #default="{ row }">
            <span>{{ row.platform_rate }}%</span>
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑佣金配置' : '新建佣金配置'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="配置名称"><el-input v-model="form.name" placeholder="请输入名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="form.category" style="width:100%">
                <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="佣金费率(%)"><el-input-number v-model="form.rate" :min="0" :max="100" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低金额"><el-input-number v-model="form.min_amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最高金额"><el-input-number v-model="form.max_amount" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主播分成(%)"><el-input-number v-model="form.anchor_rate" :min="0" :max="100" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="平台分成(%)"><el-input-number v-model="form.platform_rate" :min="0" :max="100" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="启用状态">
              <el-switch v-model="form.is_active" />
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
