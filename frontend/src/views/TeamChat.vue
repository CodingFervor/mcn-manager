<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { TeamChatAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, total_members: 0, total_messages: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', channel_type: '', is_active: '' })

const channelTypeMap = { group: '群组', direct: '私聊', announcement: '公告' }
const channelTypeColor = { group: 'primary', direct: 'success', announcement: 'warning' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      TeamChatAPI.list(filters.value),
      TeamChatAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { channel_name: '', channel_type: 'group', members_count: 0, messages_count: 0, last_message: '', is_active: true }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await TeamChatAPI.update(editingId.value, form.value)
  else await TeamChatAPI.create(form.value)
  ElMessage.success('保存成功')
  dialog.value = false
  load()
}

const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除频道「${row.channel_name}」？`, '提示', { type: 'warning' })
  await TeamChatAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="团队沟通" subtitle="频道管理 · 群组聊天 · 公告发布" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">频道总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">总成员数</div>
        <div class="stat-value">{{ stats.total_members }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">总消息数</div>
        <div class="stat-value">{{ Number(stats.total_messages || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索频道名称" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.channel_type" placeholder="频道类型" clearable @change="load" style="width: 130px">
        <el-option v-for="(v, k) in channelTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.is_active" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option label="活跃" value="true" />
        <el-option label="不活跃" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex: 1"></div>
      <el-button type="success" @click="openCreate">+ 创建频道</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="channel_name" label="频道名称" min-width="160" show-overflow-tooltip fixed />
        <el-table-column label="频道类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="channelTypeColor[row.channel_type]">{{ channelTypeMap[row.channel_type] || row.channel_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="members_count" label="成员数" width="90">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">{{ row.members_count }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="messages_count" label="消息数" width="100">
          <template #default="{ row }">{{ Number(row.messages_count || 0).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="last_message" label="最新消息" min-width="200" show-overflow-tooltip />
        <el-table-column label="活跃状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">
              <span class="status-dot" :class="row.is_active ? 'status-online' : 'status-offline'"></span>
              {{ row.is_active ? '活跃' : '不活跃' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑频道' : '创建频道'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="频道名称"><el-input v-model="form.channel_name" placeholder="请输入频道名称" /></el-form-item>
        <el-form-item label="频道类型">
          <el-select v-model="form.channel_type" style="width: 100%">
            <el-option v-for="(v, k) in channelTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="成员数"><el-input-number v-model="form.members_count" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="消息数"><el-input-number v-model="form.messages_count" :min="0" style="width: 100%" /></el-form-item>
        <el-form-item label="最新消息"><el-input v-model="form.last_message" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="活跃状态">
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
