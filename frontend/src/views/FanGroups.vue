<script setup>
import { ref, onMounted } from 'vue'
import { FanGroupAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const groups = ref([])
const stats = ref({ total_groups: 0, active_groups: 0, total_members: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

const platformMap = {
  wechat: '微信', douyin: '抖音', kuaishou: '快手',
  xiaohongshu: '小红书', qq: 'QQ', other: '其他'
}
const platformColor = {
  wechat: 'success', douyin: 'danger', kuaishou: 'warning',
  xiaohongshu: '', qq: 'info', other: 'info'
}
const statusColor = { active: 'success', inactive: 'warning', disbanded: 'danger' }
const statusLabel = { active: '活跃', inactive: '停用', disbanded: '已解散' }

async function loadStats() {
  try { stats.value = await FanGroupAPI.stats() } catch { stats.value = { total_groups: 0, active_groups: 0, total_members: 0 } }
}

async function load() {
  loading.value = true
  try { groups.value = await FanGroupAPI.list(filters.value) }
  finally { loading.value = false }
}

const openCreate = () => {
  form.value = { platform: 'wechat', member_count: 0, status: 'active' }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  if (form.value.id) await FanGroupAPI.update(form.value.id, form.value)
  else await FanGroupAPI.create(form.value)
  dialog.value = false
  load()
  loadStats()
}

const remove = async (id) => { await FanGroupAPI.remove(id); load(); loadStats() }

onMounted(() => { load(); loadStats() })
</script>

<template>
  <div class="page">
    <PageHeader title="粉丝群管理" subtitle="社群运营 · 粉丝管理 · 群组维护" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-icon">👥</div>
        <div class="stat-label">总群数</div>
        <div class="stat-value">{{ stats.total_groups || 0 }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-icon">✅</div>
        <div class="stat-label">活跃群数</div>
        <div class="stat-value">{{ stats.active_groups || 0 }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-icon">👤</div>
        <div class="stat-label">总成员数</div>
        <div class="stat-value">{{ Number(stats.total_members || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索群名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:120px">
        <el-option label="活跃" value="active" />
        <el-option label="停用" value="inactive" />
        <el-option label="已解散" value="disbanded" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建粉丝群</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="groups" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="群名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="平台" width="100">
          <template #default="{ row }">
            <el-tag :type="platformColor[row.platform]" size="small">{{ platformMap[row.platform] || row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="store_name" label="关联店铺" width="140" show-overflow-tooltip />
        <el-table-column label="成员数" width="90">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">{{ Number(row.member_count || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="admin_name" label="管理员" width="100" />
        <el-table-column prop="tags" label="标签" width="140" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusLabel[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="粉丝群" width="580px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="群名称"><el-input v-model="form.name" placeholder="请输入群名称" /></el-form-item>
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option label="微信" value="wechat" />
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="QQ" value="qq" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联店铺ID"><el-input-number v-model="form.store_id" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="成员数"><el-input-number v-model="form.member_count" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="管理员ID"><el-input-number v-model="form.admin" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="群二维码"><el-input v-model="form.qr_code_url" placeholder="二维码链接" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="标签，逗号分隔" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="活跃" value="active" />
            <el-option label="停用" value="inactive" />
            <el-option label="已解散" value="disbanded" />
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
