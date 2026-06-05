<script setup>
import { ref, onMounted } from 'vue'
import { UserPersonaAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const personas = ref([])
const stats = ref({ total: 0, by_fan_level: {}, avg_spent: 0, total_spent: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ platform: '', fan_level: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      UserPersonaAPI.list(filters.value),
      UserPersonaAPI.stats()
    ])
    personas.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: personas.value.length,
      by_fan_level: {},
      avg_spent: personas.value.length ? Math.round(personas.value.reduce((s, r) => s + (Number(r.total_spent) || 0), 0) / personas.value.length) : 0,
      total_spent: personas.value.reduce((s, r) => s + (Number(r.total_spent) || 0), 0),
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { user_id: '', platform: 'douyin', nickname: '', gender: 'unknown', age_range: '', city: '', tags: '', total_spent: 0, order_count: 0, fan_level: 'new' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row, tags: typeof row.tags === 'object' ? JSON.stringify(row.tags) : (row.tags || '') }
  dialog.value = true
}
async function save() {
  try {
    const payload = { ...form.value }
    if (typeof payload.tags === 'string' && payload.tags.trim()) {
      try { payload.tags = JSON.parse(payload.tags) } catch { payload.tags = payload.tags }
    }
    if (form.value.id) await UserPersonaAPI.update(form.value.id, payload)
    else await UserPersonaAPI.create(payload)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此用户画像？', '提示', { type: 'warning' })
  await UserPersonaAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const platformMap = { douyin: '抖音', kuaishou: '快手', taobao: '淘宝', xiaohongshu: '小红书' }
const genderMap = { male: '男', female: '女', unknown: '未知' }
const genderColor = { male: 'primary', female: 'danger', unknown: 'info' }
const fanLevelMap = { new: '新粉', regular: '普通', loyal: '铁粉', vip: 'VIP' }
const fanLevelColor = { new: 'info', regular: '', loyal: 'success', vip: 'warning' }

const fmtNum = (n) => {
  const v = Number(n) || 0
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : v.toLocaleString()
}
const fmtMoney = (v) => {
  const n = Number(v) || 0
  return n >= 10000 ? (n / 10000).toFixed(1) + '万' : n.toFixed(0)
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="用户画像" subtitle="观众分析 · 买家标签 · VIP管理" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">用户总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">粉丝层级</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Object.keys(stats.by_fan_level || {}).length }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">人均消费</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ fmtMoney(stats.avg_spent) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总消费额</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ fmtMoney(stats.total_spent) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索昵称/用户ID" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.platform" placeholder="平台" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.fan_level" placeholder="粉丝等级" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in fanLevelMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 添加用户</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="personas" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="nickname" label="昵称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="user_id" label="用户ID" width="130" show-overflow-tooltip />
        <el-table-column label="平台" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ platformMap[row.platform] || row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="性别" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="genderColor[row.gender]" size="small">{{ genderMap[row.gender] || row.gender }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="age_range" label="年龄段" width="80" />
        <el-table-column prop="city" label="城市" width="80" />
        <el-table-column label="标签" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color:#a8b2d1">{{ typeof row.tags === 'object' ? JSON.stringify(row.tags) : row.tags }}</span>
          </template>
        </el-table-column>
        <el-table-column label="总消费" width="110" align="right">
          <template #default="{ row }"><span style="color:#00ff9d;font-weight:600">¥{{ fmtMoney(row.total_spent) }}</span></template>
        </el-table-column>
        <el-table-column prop="order_count" label="订单数" width="80" align="right" />
        <el-table-column prop="last_active" label="最近活跃" width="170" />
        <el-table-column label="粉丝等级" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="fanLevelColor[row.fan_level]" size="small" effect="dark">{{ fanLevelMap[row.fan_level] || row.fan_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="用户画像" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户ID"><el-input v-model="form.user_id" /></el-form-item>
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="昵称"><el-input v-model="form.nickname" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width:100%">
            <el-option v-for="(v, k) in genderMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="年龄段"><el-input v-model="form.age_range" placeholder="如: 25-34" /></el-form-item>
        <el-form-item label="城市"><el-input v-model="form.city" /></el-form-item>
        <el-form-item label="标签">
          <el-input v-model="form.tags" type="textarea" :rows="2" placeholder='JSON数组或文本，如: ["高消费","回购用户"]' />
        </el-form-item>
        <el-form-item label="总消费"><el-input-number v-model="form.total_spent" :min="0" :precision="2" style="width:100%" /></el-form-item>
        <el-form-item label="订单数"><el-input-number v-model="form.order_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="粉丝等级">
          <el-select v-model="form.fan_level" style="width:100%">
            <el-option v-for="(v, k) in fanLevelMap" :key="k" :label="v" :value="k" />
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
