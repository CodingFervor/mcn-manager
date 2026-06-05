<script setup>
import { ref, onMounted } from 'vue'
import { OpinionAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, negative: 0, escalated: 0 })
const loading = ref(false)
const dialog = ref(false)
const resolveDialog = ref(false)
const form = ref({})
const resolveForm = ref({})
const filters = ref({ kw: '', status: '', sentiment: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      OpinionAPI.list(filters.value),
      OpinionAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    title: '', source: '', url: '', content: '', sentiment: 'neutral',
    related_store: null, related_anchor: null, heat: 0, discovered_at: ''
  }
  dialog.value = true
}

async function save() {
  await OpinionAPI.create(form.value)
  dialog.value = false
  load()
}

const openResolve = (row) => {
  resolveForm.value = { id: row.id, resolution: '' }
  resolveDialog.value = true
}

async function submitResolve() {
  await OpinionAPI.resolve(resolveForm.value.id, { resolution: resolveForm.value.resolution })
  resolveDialog.value = false
  load()
}

const sourceMap = { weibo: '微博', douyin: '抖音', xiaohongshu: '小红书', wechat: '微信', taobao: '淘宝', other: '其他' }
const sentimentMap = { positive: '正面', neutral: '中性', negative: '负面' }
const sentimentColor = { positive: 'success', neutral: 'warning', negative: 'danger' }
const statusMap = { pending: '待处理', processing: '处理中', resolved: '已解决', escalated: '已升级' }
const statusColor = { pending: 'danger', processing: 'warning', resolved: 'success', escalated: 'primary' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="舆情监控" subtitle="舆情追踪 · 品牌口碑 · 危机预警" />

    <div class="stat-cards" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="stat-card g1">
        <div class="stat-label">舆情总数</div>
        <div class="stat-value">{{ stats.total }}</div>
      </div>
      <div class="stat-card g5">
        <div class="stat-label">负面舆情</div>
        <div class="stat-value">{{ stats.negative }}</div>
      </div>
      <div class="stat-card g4">
        <div class="stat-label">已升级</div>
        <div class="stat-value">{{ stats.escalated }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索标题/内容" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.sentiment" placeholder="情感倾向" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in statusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建舆情</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="来源" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ sourceMap[row.source_display] || row.source_display || sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="情感倾向" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="sentimentColor[row.sentiment]" effect="dark">{{ sentimentMap[row.sentiment] || row.sentiment }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="related_store_name" label="关联店铺" width="120" />
        <el-table-column prop="related_anchor_name" label="关联主播" width="100" />
        <el-table-column label="热度值" width="90">
          <template #default="{ row }">
            <span style="color: var(--neon-cyan); font-weight: 600">{{ row.heat }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="statusColor[row.status]">{{ statusMap[row.status] || row.status_display || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="handler_name" label="处理人" width="100" />
        <el-table-column prop="discovered_at" label="发现时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'pending' || row.status === 'processing'" size="small" type="warning" @click="openResolve(row)">处理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新建舆情" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" placeholder="请输入舆情标题" /></el-form-item>
        <el-form-item label="来源">
          <el-select v-model="form.source" style="width: 100%">
            <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="链接"><el-input v-model="form.url" placeholder="原文链接" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="3" placeholder="舆情内容" /></el-form-item>
        <el-form-item label="情感倾向">
          <el-select v-model="form.sentiment" style="width: 100%">
            <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联店铺ID"><el-input-number v-model="form.related_store" :min="1" /></el-form-item>
        <el-form-item label="关联主播ID"><el-input-number v-model="form.related_anchor" :min="1" /></el-form-item>
        <el-form-item label="热度值"><el-input-number v-model="form.heat" :min="0" /></el-form-item>
        <el-form-item label="发现时间">
          <el-date-picker v-model="form.discovered_at" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="resolveDialog" title="处理舆情" width="500px">
      <el-form :model="resolveForm" label-width="80px">
        <el-form-item label="处理结果"><el-input v-model="resolveForm.resolution" type="textarea" :rows="4" placeholder="请填写处理结果" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialog = false">取消</el-button>
        <el-button type="primary" @click="submitResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>
