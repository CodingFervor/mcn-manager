<script setup>
import { ref, onMounted } from 'vue'
import { DisasterRecoveryAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, rpo: 0, rto: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', dr_type: '', status: '' })

const typeMap = { hot_standby: '热备', warm_standby: '温备', cold_standby: '冷备', cloud_backup: '云备份' }
const statusMap = { active: '活跃', inactive: '未激活', testing: '测试中', failed: '异常' }
const statusColor = { active: 'success', inactive: 'info', testing: 'warning', failed: 'danger' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([DisasterRecoveryAPI.list(filters.value), DisasterRecoveryAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: list.value.filter(i => i.status === 'active').length, rpo: 15, rto: 30 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', dr_type: 'hot_standby', rpo: 15, rto: 30, config: '', status: 'active' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await DisasterRecoveryAPI.update(form.value.id, form.value)
    else await DisasterRecoveryAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此灾备方案？', '提示', { type: 'warning' })
  await DisasterRecoveryAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="灾备管理" subtitle="灾难恢复 · 业务连续性 · RPO/RTO" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">灾备数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">活跃</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">RPO(min)</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.rpo }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">RTO(min)</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.rto }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索灾备名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.dr_type" placeholder="灾备类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建灾备</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ typeMap[row.dr_type] || row.dr_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rpo" label="RPO(min)" width="100" align="center" />
        <el-table-column prop="rto" label="RTO(min)" width="100" align="center" />
        <el-table-column prop="last_test" label="最后测试" width="170" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
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

    <el-dialog v-model="dialog" title="灾备方案" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="灾备类型">
          <el-select v-model="form.dr_type" style="width:100%">
            <el-option v-for="(v, k) in typeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="RPO(分钟)"><el-input-number v-model="form.rpo" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="RTO(分钟)"><el-input-number v-model="form.rto" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="配置"><el-input v-model="form.config" type="textarea" :rows="4" placeholder="JSON格式配置" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
