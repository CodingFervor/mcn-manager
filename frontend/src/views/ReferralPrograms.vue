<script setup>
import { ref, onMounted } from 'vue'
import { ReferralProgramAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_referrals: 0, conversion_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ReferralProgramAPI.list(filters.value),
      ReferralProgramAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      total_referrals: list.value.reduce((s, i) => s + (i.total_referrals || 0), 0),
      conversion_rate: list.value.length ? (list.value.reduce((s, i) => s + (i.total_conversions || 0), 0) / Math.max(list.value.reduce((s, i) => s + (i.total_referrals || 0), 0), 1) * 100).toFixed(1) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', referrer_reward: '', referee_reward: '', total_referrals: 0,
    total_conversions: 0, budget: 0, spent: 0, is_active: true
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await ReferralProgramAPI.update(form.value.id, form.value)
    else await ReferralProgramAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="推荐计划" subtitle="裂变推广 · 邀请奖励 · 转化追踪" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">计划总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总推荐数</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_referrals }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">转化率</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.conversion_rate }}%</div>
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
        <el-table-column prop="referrer_reward" label="推荐人奖励" width="110" />
        <el-table-column prop="referee_reward" label="被推荐人奖励" width="120" />
        <el-table-column label="总推荐数" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff;font-weight:600">{{ row.total_referrals }}</span></template>
        </el-table-column>
        <el-table-column label="总转化数" width="100" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">{{ row.total_conversions }}</span></template>
        </el-table-column>
        <el-table-column label="预算" width="100" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">¥{{ fmtMoney(row.budget) }}</span></template>
        </el-table-column>
        <el-table-column label="已花费" width="100" align="right">
          <template #default="{ row }"><span style="color:#ff4d9e;font-weight:600">¥{{ fmtMoney(row.spent) }}</span></template>
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

    <el-dialog v-model="dialog" title="推荐计划" width="550px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="计划名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="推荐人奖励"><el-input v-model="form.referrer_reward" /></el-form-item>
        <el-form-item label="被推荐人奖励"><el-input v-model="form.referee_reward" /></el-form-item>
        <el-form-item label="总推荐数"><el-input-number v-model="form.total_referrals" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="总转化数"><el-input-number v-model="form.total_conversions" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="预算"><el-input-number v-model="form.budget" :min="0" :step="100" style="width:100%" /></el-form-item>
        <el-form-item label="已花费"><el-input-number v-model="form.spent" :min="0" :step="100" style="width:100%" /></el-form-item>
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
