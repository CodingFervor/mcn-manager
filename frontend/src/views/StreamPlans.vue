<script setup>
import { ref, onMounted } from 'vue'
import { StreamPlanAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const plans = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '' })

const statusMap = {
  planned: { label: '已计划', type: 'info' },
  confirmed: { label: '已确认', type: 'warning' },
  live: { label: '直播中', type: 'success' },
  completed: { label: '已完成', type: '' },
  cancelled: { label: '已取消', type: 'danger' }
}

async function load() {
  loading.value = true
  try { plans.value = await StreamPlanAPI.list(filters.value) }
  finally { loading.value = false }
}

const openCreate = () => {
  form.value = { status: 'planned', target_gmv: 0, target_viewers: 0 }
  dialog.value = true
}
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }

async function save() {
  if (form.value.id) await StreamPlanAPI.update(form.value.id, form.value)
  else await StreamPlanAPI.create(form.value)
  dialog.value = false
  load()
}

const remove = async (id) => { await StreamPlanAPI.remove(id); load() }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播预告" subtitle="排期管理 · 预告发布 · 目标设定" />

    <div class="toolbar">
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="已计划" value="planned" />
        <el-option label="已确认" value="confirmed" />
        <el-option label="直播中" value="live" />
        <el-option label="已完成" value="completed" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
      <el-button type="primary" @click="load">查询</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新建预告</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="plans" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="直播主题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="store_name" label="店铺" width="140" show-overflow-tooltip />
        <el-table-column prop="anchor_name" label="主播" width="100" />
        <el-table-column prop="co_anchor_name" label="副播" width="100" />
        <el-table-column prop="planned_start" label="开始时间" width="160" />
        <el-table-column prop="planned_end" label="结束时间" width="160" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">{{ statusMap[row.status]?.label || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="目标GMV" width="120">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">¥{{ Number(row.target_gmv || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="target_viewers" label="目标观看" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan)">{{ Number(row.target_viewers || 0).toLocaleString() }}</span>
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

    <el-dialog v-model="dialog" title="直播预告" width="620px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="直播主题"><el-input v-model="form.title" placeholder="请输入直播主题" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="店铺ID"><el-input-number v-model="form.store_id" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="房间号"><el-input-number v-model="form.room_id" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="副播ID"><el-input-number v-model="form.co_anchor" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker v-model="form.planned_start" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" placeholder="选择开始时间" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker v-model="form.planned_end" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" placeholder="选择结束时间" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="已计划" value="planned" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="直播中" value="live" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题标签"><el-input v-model="form.theme" placeholder="如：大促、日常、专场" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="目标GMV"><el-input-number v-model="form.target_gmv" :min="0" :step="1000" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标观看"><el-input-number v-model="form.target_viewers" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="3" placeholder="备注信息" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
