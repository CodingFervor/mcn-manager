<script setup>
import { ref, onMounted, computed } from 'vue'
import { FinanceAPI, ContractAPI, CommissionAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

const activeTab = ref('finance')
const loading = ref(false)
const financeList = ref([])
const contracts = ref([])
const commissions = ref([])
const summary = ref({ income: 0, expense: 0, profit: 0 })
const filters = ref({ start: '', end: '' })

async function loadFinance() {
  loading.value = true
  try {
    const [list, sum] = await Promise.all([
      FinanceAPI.list(filters.value),
      FinanceAPI.summary(filters.value),
    ])
    financeList.value = list
    summary.value = sum
  } finally { loading.value = false }
}
async function loadContracts() {
  loading.value = true
  try { contracts.value = await ContractAPI.list() } finally { loading.value = false }
}
async function loadCommissions() {
  loading.value = true
  try { commissions.value = await CommissionAPI.list() } finally { loading.value = false }
}

const settleCommission = async (id) => { await CommissionAPI.settle(id); loadCommissions() }

onMounted(() => { loadFinance(); loadContracts(); loadCommissions() })
</script>

<template>
  <div class="page">
    <PageHeader title="财务中心" subtitle="收支管理 · 佣金结算 · 合同管理" />
    <el-tabs v-model="activeTab">
      <el-tab-pane label="收支管理" name="finance">
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:20px">
          <StatCard label="总收入" :value="'¥' + (summary.income/10000).toFixed(1) + '万'" icon="💰" gradient="g3" />
          <StatCard label="总支出" :value="'¥' + (summary.expense/10000).toFixed(1) + '万'" icon="📤" gradient="g4" />
          <StatCard label="净利润" :value="'¥' + (summary.profit/10000).toFixed(1) + '万'" icon="💎" :gradient="summary.profit >= 0 ? 'g1' : 'g4'" />
        </div>
        <div class="glass" style="padding:20px">
          <el-table :data="financeList" stripe v-loading="loading">
            <el-table-column prop="date" label="日期" width="110" />
            <el-table-column prop="type_display" label="类型" width="80" />
            <el-table-column prop="category_display" label="类目" width="100" />
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="{ row }">
                <span :style="{ color: row.type === 'income' ? '#00ff9d' : '#ff4d9e', fontWeight: 600 }">
                  {{ row.type === 'income' ? '+' : '-' }}¥{{ row.amount }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="store_name" label="店铺" width="150" />
            <el-table-column prop="employee_name" label="人员" width="100" />
            <el-table-column prop="remark" label="备注" min-width="150" />
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="合同管理" name="contract">
        <div class="glass" style="padding:20px">
          <el-table :data="contracts" stripe v-loading="loading">
            <el-table-column prop="employee_name" label="员工" width="100" />
            <el-table-column prop="contract_no" label="合同编号" width="120" />
            <el-table-column prop="contract_type_display" label="类型" width="100" />
            <el-table-column prop="start_date" label="开始" width="110" />
            <el-table-column prop="end_date" label="到期" width="110" />
            <el-table-column prop="status_display" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : row.status === 'expiring' ? 'warning' : 'danger'" size="small">{{ row.status_display }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="salary" label="薪资" width="120">
              <template #default="{ row }">¥{{ row.salary }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      <el-tab-pane label="佣金结算" name="commission">
        <div class="glass" style="padding:20px">
          <el-table :data="commissions" stripe v-loading="loading">
            <el-table-column prop="employee_name" label="员工" width="100" />
            <el-table-column prop="period" label="周期" width="100" />
            <el-table-column prop="gmv" label="GMV" width="120">
              <template #default="{ row }">¥{{ row.gmv }}</template>
            </el-table-column>
            <el-table-column prop="commission" label="佣金" width="120">
              <template #default="{ row }">
                <span style="color:var(--neon-cyan);font-weight:600">¥{{ row.commission }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status_display" label="状态" width="100" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button v-if="row.status === 'pending'" size="small" type="success" @click="settleCommission(row.id)">结算</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
