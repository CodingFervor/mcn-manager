<script setup>
import { ref, onMounted } from 'vue'
import { LivePollAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_votes: 0, active: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '' })

const statusMap = { draft: '草稿', active: '进行中', closed: '已结束' }
const statusColor = { draft: 'info', active: 'success', closed: '' }

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([LivePollAPI.list(filters.value), LivePollAPI.stats()])
    list.value = data
    stats.value = st
  } catch {
    stats.value = { total: list.value.length, total_votes: 0, active: 0 }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { question: '', options: [], votes: [], total_votes: 0, status: 'draft', duration_seconds: 0 }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  try {
    if (form.value.id) await LivePollAPI.update(form.value.id, form.value)
    else await LivePollAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false; load()
  } catch { ElMessage.error('保存失败') }
}

const remove = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  await LivePollAPI.remove(row.id)
  ElMessage.success('已删除'); load()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播投票" subtitle="互动投票 · 实时统计 · 结果分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-label">投票总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-label">总投票数</div>
        <div class="stat-value">{{ Number(stats.total_votes || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-label">进行中</div>
        <div class="stat-value">{{ stats.active }}</div>
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
        <el-table-column prop="question" label="投票问题" min-width="200" show-overflow-tooltip />
        <el-table-column label="选项数" width="80">
          <template #default="{ row }">{{ Array.isArray(row.options) ? row.options.length : 0 }}</template>
        </el-table-column>
        <el-table-column label="总投票" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ row.total_votes }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时长(秒)" width="100">
          <template #default="{ row }">{{ row.duration_seconds }}s</template>
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

    <el-dialog v-model="dialog" title="投票管理" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="投票问题"><el-input v-model="form.question" placeholder="请输入投票问题" /></el-form-item>
        <el-form-item label="选项">
          <el-input v-model="form.options" type="textarea" :rows="3" placeholder="JSON格式，如：[&quot;选项A&quot;,&quot;选项B&quot;,&quot;选项C&quot;]" />
        </el-form-item>
        <el-form-item label="投票结果">
          <el-input v-model="form.votes" type="textarea" :rows="3" placeholder="JSON格式，如：[10,20,30]" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="时长(秒)"><el-input-number v-model="form.duration_seconds" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
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
