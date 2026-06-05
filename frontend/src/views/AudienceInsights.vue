<script setup>
import { ref, onMounted } from 'vue'
import { AudienceInsightAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_gender: {}, avg_watch_time: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ gender: '', kw: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      AudienceInsightAPI.list(filters.value),
      AudienceInsightAPI.stats()
    ])
    list.value = data
    stats.value = st
  } catch {
    stats.value = {
      total: list.value.length,
      by_gender: {},
      avg_watch_time: list.value.length ? (list.value.reduce((s, i) => s + (i.avg_watch_time || 0), 0) / list.value.length).toFixed(0) : 0
    }
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    age_group: '', gender: 'unknown', location: '', interest: '',
    percentage: 0, avg_watch_time: 0, spending_power: 'medium', period: ''
  }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await AudienceInsightAPI.update(form.value.id, form.value)
    else await AudienceInsightAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}

const genderMap = { male: '男', female: '女', unknown: '未知' }
const genderColor = { male: '', female: 'danger', unknown: 'info' }
const spendingMap = { low: '低', medium: '中', high: '高' }
const spendingColor = { low: 'info', medium: 'warning', high: 'success' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="受众洞察" subtitle="用户画像 · 行为分析 · 精准触达" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">洞察总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">性别分布</div>
        <div style="font-size:16px;font-weight:700;color:#00ff9d">
          <span v-for="(v, k) in stats.by_gender" :key="k" style="margin-right:12px">{{ genderMap[k] || k }}: {{ v }}</span>
          <span v-if="!stats.by_gender || !Object.keys(stats.by_gender).length">-</span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均观看时长</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.avg_watch_time }}分钟</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索年龄/地区/兴趣" style="width:220px" @keyup.enter="load" />
      <el-select v-model="filters.gender" placeholder="性别" clearable @change="load" style="width:110px">
        <el-option v-for="(v, k) in genderMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增洞察</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="age_group" label="年龄组" width="90" align="center" />
        <el-table-column label="性别" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="genderColor[row.gender]" size="small">{{ genderMap[row.gender] || row.gender }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="地区" width="100" show-overflow-tooltip />
        <el-table-column prop="interest" label="兴趣" min-width="120" show-overflow-tooltip />
        <el-table-column label="占比%" width="80" align="center">
          <template #default="{ row }">
            <span style="color:#00e5ff;font-weight:600">{{ row.percentage }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="平均观看时长" width="110" align="right">
          <template #default="{ row }"><span style="color:#ffd23f;font-weight:600">{{ row.avg_watch_time }}分钟</span></template>
        </el-table-column>
        <el-table-column label="消费力" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="spendingColor[row.spending_power]" size="small">{{ spendingMap[row.spending_power] || row.spending_power }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="统计周期" width="110" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="受众洞察" width="550px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="年龄组"><el-input v-model="form.age_group" placeholder="如: 18-24" /></el-form-item>
        <el-form-item label="性别">
          <el-select v-model="form.gender" style="width:100%">
            <el-option v-for="(v, k) in genderMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="地区"><el-input v-model="form.location" /></el-form-item>
        <el-form-item label="兴趣"><el-input v-model="form.interest" /></el-form-item>
        <el-form-item label="占比%"><el-input-number v-model="form.percentage" :min="0" :max="100" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="平均观看时长"><el-input-number v-model="form.avg_watch_time" :min="0" :precision="1" style="width:100%" /></el-form-item>
        <el-form-item label="消费力">
          <el-select v-model="form.spending_power" style="width:100%">
            <el-option v-for="(v, k) in spendingMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="统计周期"><el-input v-model="form.period" placeholder="如: 2026-Q1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
