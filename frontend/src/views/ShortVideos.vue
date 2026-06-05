<script setup>
import { ref, onMounted } from 'vue'
import { ShortVideoAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const videos = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', platform: '' })

const stats = ref({ total: 0, published: 0, total_views: 0, total_likes: 0 })

async function loadStats() {
  try {
    const s = await ShortVideoAPI.stats()
    stats.value = { total: s.total || 0, published: s.published || 0, total_views: s.total_views || 0, total_likes: s.total_likes || 0 }
  } catch {
    stats.value = {
      total: videos.value.length,
      published: videos.value.filter(i => i.status === 'published').length,
      total_views: videos.value.reduce((a, b) => a + (Number(b.views) || 0), 0),
      total_likes: videos.value.reduce((a, b) => a + (Number(b.likes) || 0), 0),
    }
  }
}

async function load() {
  loading.value = true
  try {
    videos.value = await ShortVideoAPI.list(filters.value)
    loadStats()
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = { title: '', platform: 'douyin', store: null, anchor: null, cover_url: '', video_url: '', duration: 0, script: '', tags: '', product: null, status: 'draft', creator: null, publish_time: '' }
  dialog.value = true
}
const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}
async function save() {
  try {
    if (form.value.id) await ShortVideoAPI.update(form.value.id, form.value)
    else await ShortVideoAPI.create(form.value)
    ElMessage.success('保存成功')
    dialog.value = false
    load()
  } catch { ElMessage.error('保存失败') }
}
const remove = async (row) => {
  await ElMessageBox.confirm('确定删除此视频记录？', '提示', { type: 'warning' })
  await ShortVideoAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const platformTagType = (platform) => {
  const map = { douyin: 'primary', kuaishou: 'warning', xiaohongshu: 'danger', bilibili: 'info', wechat: 'success' }
  return map[platform] || 'info'
}

const fmtNum = (v) => {
  const n = Number(v) || 0
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  if (n >= 1000) return (n / 1000).toFixed(1) + '千'
  return n.toString()
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="短视频管理" subtitle="内容创作 · 发布管理 · 数据分析" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">已发布</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.published }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总播放量</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ fmtNum(stats.total_views) }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总点赞</div>
        <div style="font-size:28px;font-weight:800;color:#ff4d9e">{{ fmtNum(stats.total_likes) }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-select v-model="filters.platform" placeholder="平台筛选" clearable @change="load" style="width:140px">
        <el-option label="抖音" value="douyin" />
        <el-option label="快手" value="kuaishou" />
        <el-option label="小红书" value="xiaohongshu" />
        <el-option label="B站" value="bilibili" />
        <el-option label="微信视频号" value="wechat" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="load" style="width:140px">
        <el-option label="草稿" value="draft" />
        <el-option label="待审核" value="pending" />
        <el-option label="已发布" value="published" />
        <el-option label="已下架" value="removed" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增视频</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="videos" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="平台" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="platformTagType(row.platform)" size="small" effect="dark">{{ row.platform_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="anchor_name" label="出镜主播" width="100" />
        <el-table-column prop="creator_name" label="制作人" width="100" />
        <el-table-column prop="duration" label="时长(秒)" width="90" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : row.status === 'pending' ? 'warning' : row.status === 'removed' ? 'danger' : 'info'" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="播放量" width="100" align="right">
          <template #default="{ row }"><span style="color:#00e5ff">{{ fmtNum(row.views) }}</span></template>
        </el-table-column>
        <el-table-column label="点赞" width="90" align="right">
          <template #default="{ row }"><span style="color:#ff4d9e">{{ fmtNum(row.likes) }}</span></template>
        </el-table-column>
        <el-table-column prop="comments" label="评论" width="80" align="right" />
        <el-table-column prop="shares" label="转发" width="80" align="right" />
        <el-table-column label="互动率%" width="100" align="center">
          <template #default="{ row }">
            <span style="color:#ffd23f">{{ row.engagement_rate }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="publish_time" label="发布时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="短视频记录" width="650px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="平台">
          <el-select v-model="form.platform" style="width:100%">
            <el-option label="抖音" value="douyin" />
            <el-option label="快手" value="kuaishou" />
            <el-option label="小红书" value="xiaohongshu" />
            <el-option label="B站" value="bilibili" />
            <el-option label="微信视频号" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="店铺ID"><el-input-number v-model="form.store" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="主播ID"><el-input-number v-model="form.anchor" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="封面URL"><el-input v-model="form.cover_url" /></el-form-item>
        <el-form-item label="视频URL"><el-input v-model="form.video_url" /></el-form-item>
        <el-form-item label="时长(秒)"><el-input-number v-model="form.duration" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="脚本"><el-input v-model="form.script" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="多个标签用逗号分隔" /></el-form-item>
        <el-form-item label="商品ID"><el-input-number v-model="form.product" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width:100%">
            <el-option label="草稿" value="draft" />
            <el-option label="待审核" value="pending" />
            <el-option label="已发布" value="published" />
            <el-option label="已下架" value="removed" />
          </el-select>
        </el-form-item>
        <el-form-item label="制作人ID"><el-input-number v-model="form.creator" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="发布时间"><el-date-picker v-model="form.publish_time" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
