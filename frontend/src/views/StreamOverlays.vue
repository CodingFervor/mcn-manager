<script setup>
import { ref, onMounted } from 'vue'
import { StreamOverlayAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const overlayTypeMap = { countdown: '倒计时', banner: '横幅', product_card: '商品卡片', poll: '投票', lottery: '抽奖', qr_code: '二维码' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([StreamOverlayAPI.list(filters.value), StreamOverlayAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, active: 0, by_type: {} }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', overlay_type: 'countdown', is_active: false }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await StreamOverlayAPI.update(form.value.id, form.value)
    else await StreamOverlayAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await StreamOverlayAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播贴片" subtitle="贴片管理 · 实时覆盖 · 互动组件" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">贴片总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">启用中</div>
        <div class="stat-value">{{ stats.active }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">类型数</div>
        <div class="stat-value">{{ Object.keys(stats.by_type || {}).length }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索" style="width:200px" @keyup.enter="load" />
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="贴片名称" min-width="180" show-overflow-tooltip />
        <el-table-column label="贴片类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ overlayTypeMap[row.overlay_type] || row.overlay_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="直播贴片" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="贴片名称"><el-input v-model="form.name" placeholder="请输入贴片名称" /></el-form-item>
        <el-form-item label="贴片类型">
          <el-select v-model="form.overlay_type" style="width:100%">
            <el-option v-for="(v, k) in overlayTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
