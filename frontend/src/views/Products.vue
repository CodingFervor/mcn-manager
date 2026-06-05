<script setup>
import { ref, onMounted } from 'vue'
import { ProductAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const products = ref([])
const loading = ref(false)
const dialog = ref(false)
const form = ref({})
const filters = ref({ status: '', kw: '' })

async function load() {
  loading.value = true
  try { products.value = await ProductAPI.list(filters.value) }
  finally { loading.value = false }
}
const openCreate = () => { form.value = { status: 'active' }; dialog.value = true }
const openEdit = (row) => { form.value = { ...row }; dialog.value = true }
async function save() {
  if (form.value.id) await ProductAPI.update(form.value.id, form.value)
  else await ProductAPI.create(form.value)
  dialog.value = false; load()
}
const remove = async (id) => { await ProductAPI.remove(id); load() }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="商品管理" subtitle="商品库管理 · 库存监控 · 佣金设置" />
    <div class="toolbar">
      <el-input v-model="filters.kw" placeholder="搜索商品名/SKU" style="width:200px" @keyup.enter="load" />
      <el-select v-model="filters.status" placeholder="状态" clearable @change="load" style="width:120px">
        <el-option label="在售" value="active" /><el-option label="下架" value="inactive" /><el-option label="草稿" value="draft" />
      </el-select>
      <el-button type="primary" @click="load">搜索</el-button>
      <el-button type="success" @click="openCreate">+ 添加商品</el-button>
    </div>
    <div class="glass" style="padding:20px">
      <el-table :data="products" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="商品名称" min-width="200" />
        <el-table-column prop="sku" label="SKU" width="100" />
        <el-table-column prop="price" label="售价" width="100">
          <template #default="{ row }">¥{{ row.price }}</template>
        </el-table-column>
        <el-table-column prop="cost" label="成本" width="80">
          <template #default="{ row }">¥{{ row.cost }}</template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80">
          <template #default="{ row }">
            <span :style="{ color: row.stock <= 10 ? '#ff4d9e' : '#00ff9d' }">{{ row.stock }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="commission_rate" label="佣金%" width="80" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'inactive' ? 'danger' : 'info'" size="small">{{ row.status === 'active' ? '在售' : row.status === 'inactive' ? '下架' : '草稿' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="dialog" title="商品" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="商品名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="SKU"><el-input v-model="form.sku" /></el-form-item>
        <el-form-item label="售价"><el-input-number v-model="form.price" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="成本价"><el-input-number v-model="form.cost" :min="0" :precision="2" /></el-form-item>
        <el-form-item label="库存"><el-input-number v-model="form.stock" :min="0" /></el-form-item>
        <el-form-item label="佣金比例%"><el-input-number v-model="form.commission_rate" :min="0" :max="100" :precision="2" /></el-form-item>
        <el-form-item label="供应商"><el-input v-model="form.supplier" /></el-form-item>
        <el-form-item label="状态"><el-select v-model="form.status"><el-option label="在售" value="active" /><el-option label="下架" value="inactive" /><el-option label="草稿" value="draft" /></el-select></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>
