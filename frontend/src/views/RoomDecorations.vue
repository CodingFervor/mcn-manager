<script setup>
import { ref, onMounted } from 'vue'
import { RoomDecorationAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const list = ref([])
const stats = ref({ total: 0, active: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ kw: '', deco_type: '', is_active: '' })

async function load() {
  loading.value = true
  try {
    const [data, st] = await Promise.all([
      RoomDecorationAPI.list(filters.value),
      RoomDecorationAPI.stats()
    ])
    list.value = data
    stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  form.value = {
    room: null, deco_type: 'background', name: '', image_url: '',
    position: 'full', is_active: true, start_time: '', end_time: '', sort_order: 0
  }
  dialog.value = true
}

const openEdit = (row) => {
  form.value = { ...row }
  dialog.value = true
}

async function save() {
  if (form.value.id) await RoomDecorationAPI.update(form.value.id, form.value)
  else await RoomDecorationAPI.create(form.value)
  dialog.value = false
  load()
}

const toggleActive = async (row) => {
  await RoomDecorationAPI.toggle(row.id, {})
  load()
}

const decoTypeMap = {
  background: '背景', overlay: '贴片', widget: '挂件',
  watermark: '水印', countdown: '倒计时', product_card: '商品卡片'
}
const positionMap = {
  top_left: '左上', top_right: '右上', bottom_left: '左下',
  bottom_right: '右下', center: '居中', full: '全屏'
}

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="直播间装修" subtitle="背景管理 · 贴片挂件 · 视觉素材" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">素材总数</div>
        <div style="font-size:28px;font-weight:800;color:#00e5ff">{{ stats.total }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">启用中</div>
        <div style="font-size:28px;font-weight:800;color:#ffd23f">{{ stats.active }}</div>
      </div>
      <div class="glass" style="padding:20px;text-align:center">
        <div style="font-size:14px;color:#a8b2d1;margin-bottom:8px">类型分布</div>
        <div style="font-size:14px;font-weight:600;color:#00ff9d;line-height:1.8">
          <span v-for="(count, t) in stats.by_type" :key="t" style="margin-right:8px">
            <el-tag size="small">{{ decoTypeMap[t] || t }}</el-tag> {{ count }}
          </span>
          <span v-if="!Object.keys(stats.by_type || {}).length">暂无数据</span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索素材名称" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.deco_type" placeholder="类型" clearable @change="load" style="width:120px">
        <el-option v-for="(v, k) in decoTypeMap" :key="k" :label="v" :value="k" />
      </el-select>
      <el-select v-model="filters.is_active" placeholder="启用状态" clearable @change="load" style="width:120px">
        <el-option label="启用" value="true" />
        <el-option label="停用" value="false" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 新建素材</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="list" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="room_name" label="直播间" width="120" show-overflow-tooltip />
        <el-table-column prop="name" label="素材名称" min-width="150" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ decoTypeMap[row.deco_type] || row.deco_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <el-image v-if="row.image_url" :src="row.image_url" style="width:40px;height:40px" fit="cover" />
            <span v-else style="color:#a8b2d1">--</span>
          </template>
        </el-table-column>
        <el-table-column label="位置" width="80">
          <template #default="{ row }">
            <span>{{ positionMap[row.position] || row.position }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="180">
          <template #default="{ row }">
            <span style="font-size:12px" v-if="row.start_time">{{ row.start_time?.slice(0, 10) }} ~ {{ row.end_time?.slice(0, 10) }}</span>
            <span v-else style="color:#a8b2d1">永久</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="70" />
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" :type="row.is_active ? 'warning' : 'success'" @click="toggleActive(row)">
              {{ row.is_active ? '停用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" :title="form.id ? '编辑素材' : '新建素材'" width="650px">
      <el-form :model="form" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="直播间ID"><el-input-number v-model="form.room" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="素材类型">
              <el-select v-model="form.deco_type" style="width:100%">
                <el-option v-for="(v, k) in decoTypeMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="素材名称"><el-input v-model="form.name" placeholder="请输入素材名称" /></el-form-item>
        <el-form-item label="图片链接"><el-input v-model="form.image_url" placeholder="图片URL" /></el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="显示位置">
              <el-select v-model="form.position" style="width:100%">
                <el-option v-for="(v, k) in positionMap" :key="k" :label="v" :value="k" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker v-model="form.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker v-model="form.end_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
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
