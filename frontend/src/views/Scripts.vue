<script setup>
import { ref, onMounted } from 'vue'
import { ScriptAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const scripts = ref([])
const salesScripts = ref([])
const loading = ref(false)
const activeTab = ref('stream')
const dialog = ref(false)
const form = ref({})

async function load() {
  loading.value = true
  try {
    scripts.value = await ScriptAPI.list()
    salesScripts.value = await ScriptAPI.salesList()
  } finally { loading.value = false }
}
const openCreate = () => { form.value = { type: 'stream' }; dialog.value = true }
const save = async () => { await ScriptAPI.create(form.value); dialog.value = false; load() }
onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播工具" subtitle="直播脚本 · 话术库 · 节目单管理" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="直播脚本" name="stream">
        <div class="toolbar">
          <el-button type="primary" @click="openCreate">+ 新建脚本</el-button>
        </div>
        <div class="glass" style="padding:20px">
          <el-table :data="scripts" stripe v-loading="loading">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="脚本标题" min-width="200" />
            <el-table-column prop="store_name" label="店铺" width="150" />
            <el-table-column prop="duration_minutes" label="时长(分)" width="100" />
            <el-table-column prop="segment_count" label="段落数" width="80" />
            <el-table-column prop="status_display" label="状态" width="100" />
            <el-table-column prop="creator_name" label="创建人" width="100" />
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="话术库" name="sales">
        <div class="glass" style="padding:20px">
          <el-table :data="salesScripts" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="title" label="话术标题" min-width="200" />
            <el-table-column prop="scene_display" label="场景" width="120" />
            <el-table-column prop="content" label="话术内容" min-width="300">
              <template #default="{ row }">
                <span style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden">{{ row.content }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="use_count" label="使用次数" width="100" />
            <el-table-column prop="rating" label="评分" width="80" />
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="dialog" title="新建脚本" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="脚本标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="预计时长"><el-input-number v-model="form.duration_minutes" :min="1" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.note" type="textarea" :rows="3" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">创建</el-button></template>
    </el-dialog>
  </div>
</template>
