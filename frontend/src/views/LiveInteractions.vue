<script setup>
import { ref, onMounted } from 'vue'
import { LiveInteractionAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_type: {}, positive: 0, negative: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', interaction_type: '', sentiment: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      LiveInteractionAPI.list(filters.value),
      LiveInteractionAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    session: null, interaction_type: 'comment', user_id: '', user_name: '',
    content: '', is_anchor: false, sentiment: 'neutral'
  }
  dialog.value = true
}

async function save() {
  await LiveInteractionAPI.create(form.value)
  dialog.value = false
  load()
}

const interactionTypeMap = {
  comment: '评论', like: '点赞', gift: '礼物', share: '分享', follow: '关注', question: '提问'
}
const sentimentMap = { positive: '正面', neutral: '中性', negative: '负面' }
const sentimentColor = { positive: 'success', neutral: 'info', negative: 'danger' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播间互动" subtitle="弹幕管理 · 互动分析 · 情感监控" />

    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">互动总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">类型分布</div>
        <div style="font-size:14px;font-weight:600;color:#ffd23f;line-height:1.8">
          <span v-for="(count, t) in stats.by_type" :key="t" style="margin-right:8px">
            <el-tag size="small">{{ interactionTypeMap[t] || t }}</el-tag> {{ count }}
          </span>
          <span v-if="!Object.keys(stats.by_type || {}).length">暂无数据</span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">正面互动</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.positive }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">负面互动</div>
        <div style="font-size:28px;font-weight:800;color:#7c5cff">{{ stats.negative }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索用户/内容" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.interaction_type" placeholder="互动类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in interactionTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.sentiment" placeholder="情感倾向" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 新增互动</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="session_title" label="直播场次" min-width="150" show-overflow-tooltip />
        <el-table-column label="互动类型" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ interactionTypeMap[row.interaction_type] || row.interaction_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip />
        <el-table-column label="主播" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_anchor" size="small" type="danger" effect="dark">主播</el-tag>
            <span v-else style="color:#a8b2d1">--</span>
          </template>
        </el-table-column>
        <el-table-column label="情感" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="sentimentColor[row.sentiment]">{{ sentimentMap[row.sentiment] || row.sentiment }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="时间" width="170" />
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="新增互动记录" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="场次ID"><el-input-number v-model="form.session" :min="1" style="width:100%" /></el-form-item>
        <el-form-item label="互动类型">
          <el-select v-model="form.interaction_type" style="width:100%">
            <el-option v-for="(v, k) in interactionTypeMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="用户ID"><el-input v-model="form.user_id" placeholder="用户ID" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="用户昵称"><el-input v-model="form.user_name" placeholder="用户昵称" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="3" placeholder="互动内容" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="是否主播">
              <el-switch v-model="form.is_anchor" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="情感倾向">
              <el-select v-model="form.sentiment" style="width:100%">
                <el-option v-for="(v, k) in sentimentMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>
