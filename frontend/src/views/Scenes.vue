<script setup>
import { ref, onMounted } from 'vue'
import { SceneAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, active: 0, total_usage: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', scene_type: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SceneAPI.list(filters.value),
      SceneAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    name: '', scene_type: 'standard', room: null, store: null, description: '',
    cover_url: '', background_color: '', props_list: '', lighting_plan: '',
    setup_guide: '', status: 'draft', setup_time: 0, cost: 0
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await SceneAPI.update(form.value.id, form.value)
  else await SceneAPI.create(form.value)
  dialog.value = false
  load()
}

const activateItem = async (row) => {
  await SceneAPI.activate(row.id, {})
  load()
}

const sceneTypeMap = { standard: '标准', festival: '节日', brand: '品牌', outdoor: '户外', warehouse: '仓库', other: '其他' }
const statusMap = { draft: '草稿', active: '启用', inactive: '停用', archived: '归档' }
const statusColor = { draft: 'info', active: 'success', inactive: 'warning', archived: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播场景" subtitle="场景管理 · 装修模板 · 搭建方案" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">场景总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">启用中</div>
        <div class="stat-value">{{ stats.active }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总使用次数</div>
        <div class="stat-value">{{ stats.total_usage }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索场景名称" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.scene_type" placeholder="场景类型" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in sceneTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建场景</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="场景名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ sceneTypeMap[row.scene_type] || row.scene_type_display || row.scene_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="room_name" label="直播间" width="120" />
        <el-table-column prop="store_name" label="关联店铺" width="120" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="搭建耗时" width="100">
          <template #default="{ row }">
            <span>{{ row.setup_time }} min</span>
          </template>
        </el-table-column>
        <el-table-column label="搭建成本" width="100">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">¥{{ row.cost }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="usage_count" label="使用次数" width="90" />
        <el-table-column prop="last_used_at" label="最后使用" width="170" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status !== 'active'" size="small" type="success" @click="activateItem(row)">启用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑场景' : '新建场景'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="场景名称"><el-input v-model="form.name" placeholder="请输入场景名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场景类型">
              <el-select v-model="form.scene_type" style="width: 100%">
                <el-option v-for="(v, k) in sceneTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="直播间ID"><el-input-number v-model="form.room" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width: 100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述"><el-input v-model="form.description" type="textarea" placeholder="场景描述" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="封面链接"><el-input v-model="form.cover_url" placeholder="封面图片URL" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="背景色"><el-input v-model="form.background_color" placeholder="如 #1a1a2e" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="道具清单"><el-input v-model="form.props_list" type="textarea" placeholder="道具列表" /></el-form-item>
        <el-form-item label="灯光方案"><el-input v-model="form.lighting_plan" type="textarea" placeholder="灯光布置方案" /></el-form-item>
        <el-form-item label="搭建指南"><el-input v-model="form.setup_guide" type="textarea" :rows="3" placeholder="搭建步骤指南" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width: 100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="搭建耗时"><el-input-number v-model="form.setup_time" :min="0" style="width: 100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="搭建成本"><el-input-number v-model="form.cost" :min="0" :precision="2" style="width: 100%" /></el-form-item>
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
