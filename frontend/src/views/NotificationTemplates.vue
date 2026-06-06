<script setup>
import { ref, onMounted } from 'vue'
import { NotificationTemplateAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, email: 0, sms: 0, wechat: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', channel: '', is_active: '' })

const channelMap = { email: '邮件', sms: '短信', wechat: '微信', push: '推送', dingtalk: '钉钉' }
const channelColor = { email: 'primary', sms: 'success', wechat: 'success', push: 'warning', dingtalk: 'info' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([NotificationTemplateAPI.list(filters.value), NotificationTemplateAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, email: list.value.filter(i => i.channel === 'email').length, sms: list.value.filter(i => i.channel === 'sms').length, wechat: list.value.filter(i => i.channel === 'wechat').length }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { name: '', code: '', channel: 'email', subject: '', content: '', variables: '', is_active: true }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function handleSave() {
  try {
    if (form.value.id) await NotificationTemplateAPI.update(form.value.id, form.value)
    else await NotificationTemplateAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除此模板？', '提示', { type: 'warning' })
  await NotificationTemplateAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="通知模板" subtitle="消息模板 · 多渠道通知 · 变量管理" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">模板数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">邮件</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.email }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">短信</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.sms }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">微信</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.wechat }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索模板名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.channel" placeholder="渠道" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in channelMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建模板</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="code" label="代码" width="140" show-overflow-tooltip />
        <el-table-column label="渠道" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="channelColor[row.channel]" size="small" effect="dark">{{ channelMap[row.channel] || row.channel }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="主题" width="160" show-overflow-tooltip />
        <el-table-column prop="variable_count" label="变量数" width="80" align="center" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
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

    <el-dialog v-model="dialog" title="通知模板" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.code" /></el-form-item>
        <el-form-item label="渠道">
          <el-select v-model="form.channel" style="width:100%">
            <el-option v-for="(v, k) in channelMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题"><el-input v-model="form.subject" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="5" placeholder="使用 {{variable}} 作为变量占位符" /></el-form-item>
        <el-form-item label="变量"><el-input v-model="form.variables" type="textarea" :rows="2" placeholder="变量列表，逗号分隔" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
