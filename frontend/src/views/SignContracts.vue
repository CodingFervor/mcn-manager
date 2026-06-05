<script setup>
import { ref, onMounted } from 'vue'
import { SignContractAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, active: 0, expiring_soon: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const actionDialog = ref(false)
const actionType = ref('')
const currentRow = ref(null)
const form = ref({})
const actionForm = ref({})
const filters = ref({ kw: '', status: '', contract_type: '' })

const contractTypeMap = { new: '新签', renew: '续约', terminate: '终止' }
const statusMap = { pending: '待审批', active: '生效中', expired: '已到期', terminated: '已终止' }
const statusColor = { pending: 'warning', active: 'success', expired: 'info', terminated: 'danger' }

async function loadStats() {
  try {
    const s = await SignContractAPI.stats()
    stats.value = { total: s.total || 0, active: s.active || 0, expiring_soon: s.expiring_soon || 0, by_type: s.by_type || {} }
  } catch {
    stats.value = {
      total: list.value.length,
      active: list.value.filter(i => i.status === 'active').length,
      expiring_soon: list.value.filter(i => i.status === 'active').length,
      by_type: {}
    }
  }
}

async function load() {
  loading.value = true
  try {
    list.value = await SignContractAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    anchor: null, contract_type: 'new', start_date: '', end_date: '',
    revenue_share: 0, base_salary: 0, min_live_hours: 0, min_sessions: 0,
    penalty_clause: '', special_terms: '', status: 'pending'
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  try {
    if (form.value.id) await SignContractAPI.update(form.value.id, form.value)
    else await SignContractAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const openApprove = (row) => {
  currentRow.value = row
  actionType.value = 'approve'
  actionForm.value = { remark: '' }
  actionDialog.value = true
}

const openTerminate = (row) => {
  currentRow.value = row
  actionType.value = 'terminate'
  actionForm.value = { reason: '', remark: '' }
  actionDialog.value = true
}

async function submitAction() {
  try {
    if (actionType.value === 'approve') {
      await SignContractAPI.approve(currentRow.value.id, actionForm.value)
      ElMessage.success('已审批通过')
    } else {
      if (!actionForm.value.reason) { ElMessage.warning('请填写终止原因'); return }
      await SignContractAPI.terminate(currentRow.value.id, actionForm.value)
      ElMessage.success('已终止合同')
    }
    actionDialog.value = false
    load()
  } catch { ElMessage.error('操作失败') }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="MCN签约管理" subtitle="主播签约 · 续约管理 · 合同到期提醒" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">合同总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">生效中</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">即将到期</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.expiring_soon }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">新签/续约</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ (stats.by_type.new || 0) + (stats.by_type.renew || 0) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索主播/合同" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.contract_type" placeholder="合同类型" clearable @change="load" style="width:130px">
        <el-option v-for="(v, k) in contractTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建签约</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="anchor_name" label="主播" min-width="120" show-overflow-tooltip />
        <el-table-column label="合同类型" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ contractTypeMap[row.contract_type] || row.contract_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="合同周期" width="200">
          <template #default="{ row }">
            <span>{{ row.start_date }} ~ {{ row.end_date }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分成比例" width="90" align="center">
          <template #default="{ row }">
            <span style="color:#00e5ff;font-weight:600">{{ row.revenue_share }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="底薪" width="100" align="center">
          <template #default="{ row }">
            <span style="color:#00ff9d;font-weight:600">¥{{ Number(row.base_salary || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="min_live_hours" label="最低时长(h)" width="110" align="center" />
        <el-table-column prop="min_sessions" label="最低场次" width="100" align="center" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusColor[row.status]" size="small">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="success" @click="openApprove(row)">审批</el-button>
            <el-button v-if="row.status === 'active'" size="small" type="danger" @click="openTerminate(row)">终止</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑签约' : '新建签约'" width="700px">
      <el-form :model="form" label-width="110px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="合同类型">
              <el-select v-model="form.contract_type" style="width:100%">
                <el-option v-for="(v, k) in contractTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
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
            <el-form-item label="分成比例%">
              <el-input-number v-model="form.revenue_share" :min="0" :max="100" :precision="1" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="底薪">
              <el-input-number v-model="form.base_salary" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="最低直播时长">
              <el-input-number v-model="form.min_live_hours" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最低直播场次">
              <el-input-number v-model="form.min_sessions" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="违约条款"><el-input v-model="form.penalty_clause" type="textarea" :rows="2" placeholder="违约条款说明" /></el-form-item>
        <el-form-item label="特殊条款"><el-input v-model="form.special_terms" type="textarea" :rows="2" placeholder="特殊约定条款" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="actionDialog" :title="actionType === 'approve' ? '审批合同' : '终止合同'" width="500px">
      <el-form :model="actionForm" label-width="100px">
        <el-form-item v-if="actionType === 'terminate'" label="终止原因">
          <el-input v-model="actionForm.reason" type="textarea" :rows="3" placeholder="请填写终止原因" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="actionForm.remark" type="textarea" :rows="3" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialog = false">取消</el-button>
        <el-button :type="actionType === 'approve' ? 'success' : 'danger'" @click="submitAction">{{ actionType === 'approve' ? '确认审批' : '确认终止' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
