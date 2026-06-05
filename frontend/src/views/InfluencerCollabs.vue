<script setup>
import { ref, onMounted } from 'vue'
import { InfluencerCollabAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_status: {}, expected_gmv: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', collab_type: '', status: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      InfluencerCollabAPI.list(filters.value),
      InfluencerCollabAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    influencer_name: '', platform: '', followers: 0, collab_type: 'commission',
    fee: 0, status: 'negotiating', expected_gmv: 0, actual_gmv: 0
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await InfluencerCollabAPI.update(form.value.id, form.value)
  else await InfluencerCollabAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该合作记录？', '提示', { type: 'warning' })
  await InfluencerCollabAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const collabTypeMap = { commission: '佣金制', fixed_fee: '固定费用', revenue_share: '分成制' }
const statusMap = { negotiating: '洽谈中', confirmed: '已确认', live: '进行中', completed: '已完成', cancelled: '已取消' }
const statusColor = { negotiating: 'warning', confirmed: 'primary', live: 'success', completed: 'info', cancelled: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="达人合作" subtitle="达人管理 · 合作洽谈 · 效果追踪" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">合作总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">按状态</div>
        <div style="font-size:16px;font-weight:700">
          <span v-for="(v, k) in stats.by_status" :key="k" style="margin:0 4px">
            {{ statusMap[k] || k }}: <span style="color:#ffd23f">{{ v }}</span>
          </span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">预期GMV</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">¥{{ Number(stats.expected_gmv || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索达人名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.collab_type" placeholder="合作类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in collabTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建合作</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="influencer_name" label="达人名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="platform" label="平台" width="80" />
        <el-table-column label="粉丝数" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">{{ Number(row.followers || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="合作类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ collabTypeMap[row.collab_type] || row.collab_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="费用" width="100">
          <template #default="{ row }">
            <span style="font-weight:600">¥{{ Number(row.fee || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预期GMV" width="110">
          <template #default="{ row }">
            <span style="color:#ffd23f;font-weight:600">¥{{ Number(row.expected_gmv || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="实际GMV" width="110">
          <template #default="{ row }">
            <span style="color:#00ff9d;font-weight:600">¥{{ Number(row.actual_gmv || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="removeItem(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑合作' : '新建合作'" width="750px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="达人名称"><el-input v-model="form.influencer_name" placeholder="请输入达人名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平台"><el-input v-model="form.platform" placeholder="所在平台" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="粉丝数"><el-input-number v-model="form.followers" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合作类型">
              <el-select v-model="form.collab_type" style="width:100%">
                <el-option v-for="(v, k) in collabTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="合作费用"><el-input-number v-model="form.fee" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="form.status" style="width:100%">
                <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="预期GMV"><el-input-number v-model="form.expected_gmv" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实际GMV"><el-input-number v-model="form.actual_gmv" :min="0" :precision="2" style="width:100%" /></el-form-item>
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
