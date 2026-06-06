<script setup>
import { ref, onMounted } from 'vue'
import { FeatureFlagAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, enabled: 0, gradual: 0, full: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', is_enabled: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([FeatureFlagAPI.list(filters.value), FeatureFlagAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, enabled: list.value.filter(i => i.is_enabled).length, gradual: list.value.filter(i => i.is_enabled && i.rollout_percentage < 100).length, full: list.value.filter(i => i.is_enabled && i.rollout_percentage >= 100).length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', code: '', description: '', is_enabled: false, target_users: '', rollout_percentage: 0 }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await FeatureFlagAPI.update(form.value.id, form.value)
    else await FeatureFlagAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此功能开关？', '提示', { type: 'warning' })
  await FeatureFlagAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}
const toggleFlag = async (row) => {
  await FeatureFlagAPI.update(row.id, { ...row, is_enabled: !row.is_enabled })
  ElMessage.success(row.is_enabled ? '已关闭' : '已开启')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="功能开关" subtitle="功能发布 · 灰度控制 · A/B切换" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">开关数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已启用</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.enabled }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">灰度发布</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.gradual }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">全量发布</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.full }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索功能名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.is_enabled" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option label="已启用" value="true" />
        <el-option label="已关闭" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建开关</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="code" label="代码" width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" width="160" show-overflow-tooltip />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch :model-value="row.is_enabled" @change="toggleFlag(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="target_user_count" label="目标用户数" width="100" align="right" />
        <el-table-column label="灰度比例" width="120" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.rollout_percentage >= 100 ? '#00ff9d' : row.rollout_percentage > 0 ? '#ffd23f' : '#a8b2d1', fontWeight: 700 }">{{ row.rollout_percentage }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="功能开关" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_enabled" /></el-form-item>
        <el-form-item label="目标用户"><el-input v-model="form.target_users" type="textarea" :rows="2" placeholder="用户ID列表，逗号分隔" /></el-form-item>
        <el-form-item label="灰度比例">
          <el-slider v-model="form.rollout_percentage" :min="0" :max="100" :step="5" show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
