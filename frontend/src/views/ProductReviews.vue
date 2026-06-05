<script setup>
import { ref, onMounted } from 'vue'
import { ProductReviewAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, by_sentiment: {}, avg_rating: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', sentiment: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ProductReviewAPI.list(filters.value),
      ProductReviewAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    product_name: '', rating: 5, content: '', reviewer: '',
    source: '', sentiment: 'neutral', is_replied: false
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await ProductReviewAPI.update(form.value.id, form.value)
  else await ProductReviewAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const sentimentMap = { positive: '好评', neutral: '中评', negative: '差评' }
const sentimentColor = { positive: 'success', neutral: 'warning', negative: 'danger' }
const sourceMap = { taobao: '淘宝', jd: '京东', douyin: '抖音', pdd: '拼多多', own: '自营' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="商品评价" subtitle="评价管理 · 情感分析 · 回复跟踪" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">评价总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">情感分布</div>
        <div style="font-size:18px;font-weight:700">
          <span v-for="(v, k) in stats.by_sentiment" :key="k" style="margin:0 6px">
            <span :style="{ color: k === 'positive' ? '#00ff9d' : k === 'negative' ? '#ff4757' : '#ffd23f' }">{{ sentimentMap[k] || k }}: {{ v }}</span>
          </span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均评分</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Number(stats.avg_rating || 0).toFixed(1) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品/评价者" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.sentiment" placeholder="情感" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建评价</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="product_name" label="商品名称" min-width="140" show-overflow-tooltip />
        <el-table-column label="评分" width="160">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容" min-width="180" show-overflow-tooltip />
        <el-table-column prop="reviewer" label="评价者" width="100" />
        <el-table-column label="来源" width="80">
          <template #default="{ row }">
            <el-tag size="small">{{ sourceMap[row.source] || row.source }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="情感" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="sentimentColor[row.sentiment]">{{ sentimentMap[row.sentiment] || row.sentiment }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="已回复" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_replied ? 'success' : 'info'">{{ row.is_replied ? '已回复' : '未回复' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑评价' : '新建评价'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品名称"><el-input v-model="form.product_name" placeholder="请输入商品名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="评价者"><el-input v-model="form.reviewer" placeholder="评价者" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="评分">
              <el-rate v-model="form.rating" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="来源">
              <el-select v-model="form.source" style="width:100%">
                <el-option v-for="(v, k) in sourceMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="评价内容"><el-input v-model="form.content" type="textarea" :rows="3" placeholder="评价内容" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="情感">
              <el-select v-model="form.sentiment" style="width:100%">
                <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="已回复">
              <el-switch v-model="form.is_replied" />
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
