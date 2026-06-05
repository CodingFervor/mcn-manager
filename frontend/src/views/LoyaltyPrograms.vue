<script setup>
import { ref, onMounted } from 'vue'
import { LoyaltyProgramAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_members: 0, active_members: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      LoyaltyProgramAPI.list(filters.value),
      LoyaltyProgramAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      total_members: list.value.reduce((s, i) => s + (i.total_members || 0), 0),
      active_members: list.value.reduce((s, i) => s + (i.active_members || 0), 0)
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', points_per_yuan: 1, min_points: 0, reward_type: 'discount',
    reward_value: 0, total_members: 0, active_members: 0, is_active: true
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await LoyaltyProgramAPI.update(form.value.id, form.value)
    else await LoyaltyProgramAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const rewardTypeMap = { discount: '折扣', gift: '礼品', cashback: '返现' }
const rewardTypeColor = { discount: 'warning', gift: 'success', cashback: '' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="会员积分" subtitle="积分体系 · 会员管理 · 权益激励" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">计划总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总会员数</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_members }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活跃会员</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.active_members }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索计划名称" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建计划</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="计划名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="每元积分" width="90" align="center">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:600">{{ row.points_per_yuan }}</span></template>
        </el-table-column>
        <el-table-column label="最低积分" width="90" align="right">
          <template #default="{ row }">{{ row.min_points }}</template>
        </el-table-column>
        <el-table-column label="奖励类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="rewardTypeColor[row.reward_type]" size="small">{{ rewardTypeMap[row.reward_type] || row.reward_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="奖励价值" width="90" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">{{ row.reward_value }}</span></template>
        </el-table-column>
        <el-table-column label="总会员" width="90" align="right">
          <template #default="{ row }"><span style="color:#7c5cff;font-weight:600">{{ row.total_members }}</span></template>
        </el-table-column>
        <el-table-column label="活跃会员" width="90" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ row.active_members }}</span></template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="会员积分计划" width="550px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="计划名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="每元积分"><el-input-number v-model="form.points_per_yuan" :min="0" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="最低积分"><el-input-number v-model="form.min_points" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="奖励类型">
          <el-select v-model="form.reward_type" style="width:100%">
            <el-option v-for="(v, k) in rewardTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="奖励价值"><el-input-number v-model="form.reward_value" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="总会员数"><el-input-number v-model="form.total_members" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="活跃会员"><el-input-number v-model="form.active_members" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
