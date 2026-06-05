<script setup>
import { ref, onMounted } from 'vue'
import { SocialMediaAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const stats = ref({ total: 0, total_followers: 0, avg_engagement_rate: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', platform: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      SocialMediaAPI.list(filters.value),
      SocialMediaAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    platform: '', account_name: '', followers: 0, posts_count: 0,
    avg_likes: 0, avg_comments: 0, engagement_rate: 0
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await SocialMediaAPI.update(form.value.id, form.value)
  else await SocialMediaAPI.create(form.value)
  ElMessage.success(form.value.id ? '更新成功' : '创建成功')
  dialog.value = false
  load()
}

const removeItem = async (row) => {
  await ElMessageBox.confirm('确认删除该社交账号？', '提示', { type: 'warning' })
  await SocialMediaAPI.remove(row.id)
  ElMessage.success('删除成功')
  load()
}

const platformMap = { douyin: '抖音', kuaishou: '快手', weibo: '微博', xiaohongshu: '小红书', bilibili: 'B站', wechat: '微信' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="社交媒体" subtitle="账号管理 · 数据概览 · 互动分析" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">账号总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总粉丝数</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ Number(stats.total_followers || 0).toLocaleString() }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">平均互动率</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ Number(stats.avg_engagement_rate || 0).toFixed(2) }}%</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索账号名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.platform" placeholder="平台" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建账号</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="平台" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ platformMap[row.platform] || row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="account_name" label="账号名称" min-width="130" show-overflow-tooltip />
        <el-table-column label="粉丝数" width="100">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">{{ Number(row.followers || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="posts_count" label="发布数" width="80" />
        <el-table-column label="平均点赞" width="100">
          <template #default="{ row }">
            <span style="color:#ffd23f;font-weight:600">{{ Number(row.avg_likes || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="平均评论" width="100">
          <template #default="{ row }">
            <span>{{ Number(row.avg_comments || 0).toLocaleString() }}</span>
          </template>
        </el-table-column>
        <el-table-column label="互动率" width="100">
          <template #default="{ row }">
            <span style="color:#00ff9d;font-weight:600">{{ Number(row.engagement_rate || 0).toFixed(2) }}%</span>
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

    <el-dialog v-model="dialog" :title="form.id ? '编辑社交账号' : '新建社交账号'" width="700px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="平台">
              <el-select v-model="form.platform" style="width:100%">
                <el-option v-for="(v, k) in platformMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="账号名称"><el-input v-model="form.account_name" placeholder="请输入账号名称" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="粉丝数"><el-input-number v-model="form.followers" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="发布数"><el-input-number v-model="form.posts_count" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="平均点赞"><el-input-number v-model="form.avg_likes" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平均评论"><el-input-number v-model="form.avg_comments" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="互动率(%)"><el-input-number v-model="form.engagement_rate" :min="0" :max="100" :precision="2" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
