<script setup>
import { ref, onMounted } from 'vue'
import { ScriptTagAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, by_type: {}, total_usage: 0 })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', tag_type: '', is_active: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      ScriptTagAPI.list(filters.value),
      ScriptTagAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    parent: null, name: '', color: '#00e5ff', tag_type: 'opening',
    content: '', usage_count: 0, is_active: true
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await ScriptTagAPI.update(form.value.id, form.value)
  else await ScriptTagAPI.create(form.value)
  dialog.value = false
  load()
}

const tagTypeMap = {
  opening: '开场话术', product: '产品介绍', promo: '促销话术',
  closing: '收尾话术', qa: '问答话术', story: '故事话术', other: '其他'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="话术标签库" subtitle="话术分类 · 标签管理 · 内容库" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">标签总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">类型分布</div>
        <div style="font-size:14px;font-weight:600;color:#ffd23f;line-height:1.8">
          <span v-for="(count, t) in stats.by_type" :key="t" style="margin-right:8px">
            <el-tag size="small">{{ tagTypeMap[t] || t }}</el-tag> {{ count }}
          </span>
          <span v-if="!Object.keys(stats.by_type || {}).length">暂无数据</span>
        </div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">总使用次数</div>
        <div style="font-size:28px;font-weight:800;color:#00ff9d">{{ stats.total_usage }}</div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索标签名称/内容" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.tag_type" placeholder="话术类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in tagTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.is_active" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option label="启用" value="true" />
        <el-option label="停用" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建标签</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="标签名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span :style="{ color: row.color, fontWeight: 600 }">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ tagTypeMap[row.tag_type] || row.tag_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="parent_name" label="父标签" width="120">
          <template #default="{ row }">
            <span v-if="row.parent_name" style="color:#a8b2d1">{{ row.parent_name }}</span>
            <span v-else style="color:#a8b2d1">--</span>
          </template>
        </el-table-column>
        <el-table-column label="颜色" width="70" align="center">
          <template #default="{ row }">
            <span :style="{ display:'inline-block', width:'20px', height:'20px', borderRadius:'4px', background: row.color || '#a8b2d1' }"></span>
          </template>
        </el-table-column>
        <el-table-column prop="content" label="话术内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="usage_count" label="使用次数" width="90" />
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑标签' : '新建标签'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="标签名称"><el-input v-model="form.name" placeholder="请输入标签名称" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父标签ID"><el-input-number v-model="form.parent" :min="1" style="width:100%" placeholder="留空为顶级" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="话术类型">
              <el-select v-model="form.tag_type" style="width:100%">
                <el-option v-for="(v, k) in tagTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标签颜色">
              <el-color-picker v-model="form.color" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="话术内容"><el-input v-model="form.content" type="textarea" :rows="5" placeholder="话术内容" /></el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
