<script setup>
import { ref, onMounted } from 'vue'
import { KnowledgeAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const editingId = ref(null)
const filters = ref({ kw: '', category: '', status: '' })

async function load() {
  loading.value = true
  try { list.value = await KnowledgeAPI.list(filters.value) }
  finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { title: '', category: '', content: '', tags: '', status: 'draft' }
  dialog.value = true
}

const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (editingId.value) await KnowledgeAPI.update(editingId.value, form.value)
  else await KnowledgeAPI.create(form.value)
  dialog.value = false
  load()
}

const remove = async (id) => { await KnowledgeAPI.remove(id); load() }

const publish = async (row) => {
  await KnowledgeAPI.publish(row.id)
  load()
}

const categoryMap = { sop: 'SOP流程', guide: '操作指南', template: '模板', best_practice: '最佳实践', policy: '规章制度', faq: 'FAQ' }
const knowledgeStatusMap = { draft: '草稿', published: '已发布', archived: '已归档' }
const knowledgeStatusColor = { draft: 'info', published: 'success', archived: 'warning' }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="知识库" subtitle="SOP流程 · 操作指南 · 最佳实践" />

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索标题/内容" style="width: 200px" @keyup.enter="load" />
      <el-select v-model="filters.category" placeholder="分类" clearable @change="load" style="width: 140px">
        <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width: 120px">
        <el-option v-for="(v, k) in knowledgeStatusMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建文档</el-button>
    </div>

    <div class="glass" style="padding: 20px">
      <el-table :data="list" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column label="分类" width="120">
          <template #default="{ row }">{{ categoryMap[row.category] || row.category }}</template>
        </el-table-column>
        <el-table-column prop="tags" label="标签" width="150" show-overflow-tooltip />
        <el-table-column prop="author_name" label="作者" width="100" />
        <el-table-column prop="version" label="版本" width="70" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="knowledgeStatusColor[row.status]">{{ knowledgeStatusMap[row.status] || row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览次数" width="90" />
        <el-table-column prop="updated_at" label="更新时间" width="170" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" size="small" type="success" @click="publish(row)">发布</el-button>
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="editingId ? '编辑文档' : '新建文档'" width="650px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.category" style="width: 100%">
            <el-option v-for="(v, k) in categoryMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="6" /></el-form-item>
        <el-form-item label="标签"><el-input v-model="form.tags" placeholder="多个标签用逗号分隔" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option v-for="(v, k) in knowledgeStatusMap" :key="k" :label="v" :value="k" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
