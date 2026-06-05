<script setup>
import { ref, onMounted } from 'vue'
import { GiftAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const gifts = ref([])
const stats = ref({ total_count: 0, total_value: 0, by_type: {} })
const loading = ref(false)
const dialog = ref(false)
const form = ref({})

const giftTypeMap = {
  virtual: { label: '虚拟礼物', type: 'success' },
  red_packet: { label: '红包', type: 'danger' },
  reward: { label: '打赏', type: 'warning' }
}

async function loadStats() {
  try { stats.value = await GiftAPI.stats() } catch { stats.value = { total_count: 0, total_value: 0, by_type: {} } }
}

async function load() {
  loading.value = true
  try { gifts.value = await GiftAPI.list() }
  finally { loading.value = false }
}

const openCreate = () => {
  form.value = { gift_type: 'virtual', quantity: 1, unit_value: 0 }
  dialog.value = true
}

async function save() {
  await GiftAPI.create(form.value)
  dialog.value = false
  load()
  loadStats()
}

const remove = async (id) => { await GiftAPI.remove(id); load(); loadStats() }

const fmtMoney = (v) => Number(v || 0).toLocaleString()

onMounted(() => { load(); loadStats() })
</script>

<template>
  <div class="page">
    <PageHeader title="打赏统计" subtitle="礼物追踪 · 价值统计 · 主播收益" />

    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
      <div class="stat-card g1">
        <div class="stat-icon">🎁</div>
        <div class="stat-label">礼物总数</div>
        <div class="stat-value">{{ Number(stats.total_count || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g2">
        <div class="stat-icon">💰</div>
        <div class="stat-label">总价值</div>
        <div class="stat-value">¥{{ Number(stats.total_value || 0).toLocaleString() }}</div>
      </div>
      <div class="stat-card g3">
        <div class="stat-icon">📊</div>
        <div class="stat-label">类型分布</div>
        <div class="stat-value" style="font-size:14px;line-height:1.8">
          <span v-for="(count, t) in stats.by_type" :key="t" style="margin-right:12px">
            <el-tag :type="giftTypeMap[t]?.type" size="small">{{ giftTypeMap[t]?.label || t }}</el-tag> {{ count }}
          </span>
          <span v-if="!Object.keys(stats.by_type || {}).length">暂无数据</span>
        </div>
      </div>
    </div>

    <div class="toolbar">
      <el-button type="primary" @click="load">刷新</el-button>
      <div style="flex:1"></div>
      <el-button type="success" @click="openCreate">+ 记录打赏</el-button>
    </div>

    <div class="glass" style="padding:20px">
      <el-table :data="gifts" stripe v-loading="loading" style="width:100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="session_title" label="直播场次" min-width="180" show-overflow-tooltip />
        <el-table-column prop="gift_name" label="礼物名称" width="130" />
        <el-table-column label="礼物类型" width="110">
          <template #default="{ row }">
            <el-tag :type="giftTypeMap[row.gift_type]?.type" size="small">{{ giftTypeMap[row.gift_type]?.label || row.gift_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="80">
          <template #default="{ row }">
            <span style="color:var(--neon-cyan);font-weight:600">{{ row.quantity }}</span>
          </template>
        </el-table-column>
        <el-table-column label="单价" width="100">
          <template #default="{ row }">¥{{ fmtMoney(row.unit_value) }}</template>
        </el-table-column>
        <el-table-column label="总价值" width="120">
          <template #default="{ row }">
            <span style="color:var(--neon-pink);font-weight:700">¥{{ fmtMoney(row.total_value) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sender_name" label="赠送人" width="120" />
        <el-table-column prop="created_at" label="时间" width="160" />
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="remove(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="dialog" title="记录打赏" width="520px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="场次ID"><el-input-number v-model="form.session" :min="0" style="width:100%" /></el-form-item>
        <el-form-item label="礼物名称"><el-input v-model="form.gift_name" placeholder="请输入礼物名称" /></el-form-item>
        <el-form-item label="礼物类型">
          <el-select v-model="form.gift_type" style="width:100%">
            <el-option label="虚拟礼物" value="virtual" />
            <el-option label="红包" value="red_packet" />
            <el-option label="打赏" value="reward" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="数量"><el-input-number v-model="form.quantity" :min="1" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价"><el-input-number v-model="form.unit_value" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="赠送人"><el-input v-model="form.sender_name" placeholder="赠送人昵称" /></el-form-item>
        <el-form-item label="赠送人ID"><el-input-number v-model="form.sender_id" :min="0" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
