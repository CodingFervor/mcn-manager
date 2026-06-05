<script setup>
import { ref, onMounted } from 'vue'
import { AuthorizationAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', status: '', auth_type: '' })

const authTypeMap = { brand: '品牌授权', portrait: '肖像权', copyright: '版权', music: '音乐版权', image: '图片版权', video: '视频版权' }
const statusMap = { pending: '待生效', active: '生效中', expired: '已到期', revoked: '已撤销' }
const statusColor = { pending: 'warning', active: 'success', expired: 'info', revoked: 'danger' }

async function loadStats() {
  try {
    const s = await AuthorizationAPI.stats()
    stats.value = { total: s.total || 0, active: s.active || 0, by_type: s.by_type || {} }
  } catch {
    stats.value = {
      total: list.value.length,
      active: list.value.filter(i => i.status === 'active').length,
      by_type: {}
    }
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await AuthorizationAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    auth_type: 'brand', name: '', licensor: '', licensee: '', scope: '',
    brand: null, anchor: null, start_date: '', end_date: '', file_url: '', status: 'pending'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) await AuthorizationAPI.update(form.value.id, form.value)
    else await AuthorizationAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (id) => {
  try {
    await ElMessageBox.confirm('确认删除该授权记录？', '提示', { type: 'warning' })
    await AuthorizationAPI.remove(id)
    ElMessage.success('删除成功')
    load()
  } catch {}
}

const isExpiringSoon = (row) => {
  if (row.status !== 'active' || !row.end_date) return false
  const daysLeft = Math.ceil((new Date(row.end_date) - new Date()) / (1000 * 60 * 60 * 24))
  return daysLeft >= 0 && daysLeft <= 30
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="授权管理" subtitle="品牌授权 · 版权管理 · 到期监控" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">授权总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">生效中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">品牌授权数</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.by_type.brand || 0 }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索授权名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.auth_type" placeholder="授权类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in authTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建授权</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="授权名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="授权类型" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ authTypeMap[row.auth_type] || row.auth_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="licensor" label="授权方" width="120" show-overflow-tooltip />
        <el-table-column prop="licensee" label="被授权方" width="120" show-overflow-tooltip />
        <el-table-column prop="scope" label="授权范围" min-width="140" show-overflow-tooltip />
        <el-table-column prop="brand_name" label="关联品牌" width="110" show-overflow-tooltip />
        <el-table-column prop="anchor_name" label="关联主播" width="100" show-overflow-tooltip />
        <el-table-column label="有效期" width="200">
          <template #default="{ row }">
            <span>{{ row.start_date }} ~ {{ row.end_date }}</span>
          </template>
        </el-table-column>
        <el-table-column label="到期" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="isExpiringSoon(row)" type="danger" size="small" effect="dark">即将到期</el-tag>
            <span v-else style="color:#a8b2d1;font-size:12px">--</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑授权' : '新建授权'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="授权名称"><el-input v-model="form.name" placeholder="授权名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授权类型">
              <el-select v-model="form.auth_type" style="width:100%">
                <el-option v-for="(v, k) in authTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="授权方"><el-input v-model="form.licensor" placeholder="授权方名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="被授权方"><el-input v-model="form.licensee" placeholder="被授权方名称" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="授权范围"><el-input v-model="form.scope" type="textarea" :rows="2" placeholder="授权使用范围说明" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="关联品牌ID"><el-input-number v-model="form.brand" :min="1" style="width:100%" placeholder="可选" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联主播ID"><el-input-number v-model="form.anchor" :min="1" style="width:100%" placeholder="可选" /></el-form-item>
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
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="授权文件"><el-input v-model="form.file_url" placeholder="文件链接" /></el-form-item>
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
