<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EmployeeAPI, StoreAPI, TeamAPI } from '../api'
import { Search, Plus, User, Star } from '@element-plus/icons-vue'

const list = ref([])
const stores = ref([])
const teams = ref([])
const stats = ref({ total: 0, active: 0, by_role: {} })
const loading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const detail = ref(null)
const form = ref({ name: '', role: 'anchor', phone: '', team: null, stores: [], base_salary: 8000, is_active: true, remark: '' })
const profile = ref({ nickname: '', level: '普通', style: '', category_tags: '', fans_count: 0, avg_watch: 0, conversion_rate: 0 })
const editingId = ref(null)
const filter = ref({ role: '', is_active: 'true', kw: '', team_id: '' })
const viewMode = ref('card')  // card | table

const roles = [['admin','管理员'],['manager','运营经理'],['operator','运营'],['anchor','主播'],['assistant','助理']]
const levels = ['普通', '银牌', '金牌', '王牌']
const roleGrad = { admin: 'g4', manager: 'g5', operator: 'g3', anchor: 'g1', assistant: 'g2' }

const load = async () => {
  loading.value = true
  try {
    const [emps, s, t, st] = await Promise.all([
      EmployeeAPI.list({ role: filter.value.role, is_active: filter.value.is_active, kw: filter.value.kw, team_id: filter.value.team_id }),
      StoreAPI.list(), TeamAPI.list(), EmployeeAPI.stats()
    ])
    list.value = emps; stores.value = s; teams.value = t; stats.value = st
  } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { name: '', role: 'anchor', phone: '', team: null, stores: [], base_salary: 8000, is_active: true, remark: '' }
  profile.value = { nickname: '', level: '普通', style: '', category_tags: '', fans_count: 0, avg_watch: 0, conversion_rate: 0 }
  dialogVisible.value = true
}
const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row, stores: row.store_names || [] }
  profile.value = row.anchor_profile || { ...profile.value }
  dialogVisible.value = true
}
const submit = async () => {
  const payload = { ...form.value }
  if (payload.role === 'anchor') payload.anchor_profile = { ...profile.value }
  if (editingId.value) await EmployeeAPI.update(editingId.value, payload)
  else await EmployeeAPI.create(payload)
  ElMessage.success('保存成功')
  dialogVisible.value = false
  load()
}
const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除员工「${row.name}」？`, '提示', { type: 'warning' })
  await EmployeeAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}
const showDetail = (row) => { detail.value = row; detailVisible.value = true }

const roleColor = (r) => ({ admin: 'danger', manager: 'warning', operator: 'success', anchor: 'primary', assistant: 'info' }[r] || 'info')

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">人员管理</h1>
    <div class="page-subtitle">主播档案 · 运营团队 · 小组分配</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-label">员工总数</div>
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-trend">📊 全员</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-label">在职人数</div>
          <div class="stat-value">{{ stats.active }}</div>
          <div class="stat-trend">✓ 在岗</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><Star /></el-icon>
          <div class="stat-label">主播数量</div>
          <div class="stat-value">{{ stats.by_role?.anchor || 0 }}</div>
          <div class="stat-trend">🎤 直播担当</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g5"><el-icon class="stat-icon"><User /></el-icon>
          <div class="stat-label">运营 / 经理</div>
          <div class="stat-value">{{ (stats.by_role?.operator || 0) + (stats.by_role?.manager || 0) }}</div>
          <div class="stat-trend">⚙️ 操盘手</div>
        </div>
      </el-col>
    </el-row>

    <el-card>
      <div class="toolbar">
        <el-input v-model="filter.kw" placeholder="🔍 搜索姓名/手机" style="width: 220px" clearable @keyup.enter="load" />
        <el-select v-model="filter.role" placeholder="角色" clearable style="width: 130px" @change="load">
          <el-option v-for="r in roles" :key="r[0]" :label="r[1]" :value="r[0]" />
        </el-select>
        <el-select v-model="filter.team_id" placeholder="小组" clearable style="width: 160px" @change="load">
          <el-option v-for="t in teams" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <el-segmented v-model="filter.is_active" :options="[{label:'在职',value:'true'},{label:'离职',value:'false'}]" @change="load" />
        <el-button @click="load">查询</el-button>
        <div style="flex: 1"></div>
        <el-segmented v-model="viewMode" :options="[{label:'🃏 卡片',value:'card'},{label:'📋 表格',value:'table'}]" />
        <el-button type="primary" @click="openCreate"><el-icon><Plus /></el-icon><span style="margin-left: 4px">新增</span></el-button>
      </div>

      <div v-if="viewMode === 'card'" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px">
        <div v-for="row in list" :key="row.id" class="glass" style="padding: 20px; cursor: pointer" @click="showDetail(row)">
          <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
            <div :class="`stat-card ${roleGrad[row.role]}`" style="width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 700; padding: 0; flex-shrink: 0">
              {{ row.name[0] }}
            </div>
            <div style="flex: 1; min-width: 0">
              <div style="display: flex; align-items: center; gap: 6px">
                <span style="font-weight: 700; color: white; font-size: 15px">{{ row.name }}</span>
                <span v-if="row.anchor_profile" class="live-dot" style="background: var(--neon-pink); box-shadow: 0 0 8px var(--neon-pink)"></span>
              </div>
              <el-tag size="small" :type="roleColor(row.role)" effect="dark" style="margin-top: 4px">
                {{ row.role_display }}
              </el-tag>
            </div>
          </div>
          <div v-if="row.anchor_profile" style="background: rgba(124, 92, 255, 0.08); padding: 10px; border-radius: 10px; margin-bottom: 12px">
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px">直播昵称 · {{ row.anchor_profile.nickname }}</div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap">
              <el-tag size="small" effect="dark" :type="row.anchor_profile.level === '王牌' ? 'danger' : row.anchor_profile.level === '金牌' ? 'warning' : 'primary'">
                {{ row.anchor_profile.level }}
              </el-tag>
              <span style="font-size: 11px; color: var(--text-secondary)">粉丝 {{ (row.anchor_profile.fans_count/10000).toFixed(1) }}w</span>
              <span style="font-size: 11px; color: var(--text-secondary)">场均 {{ row.anchor_profile.avg_watch }}</span>
            </div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--text-muted); margin-bottom: 8px">
            <span>📞 {{ row.phone }}</span>
            <span v-if="row.team_name">👥 {{ row.team_name }}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border-glow)">
            <span style="font-size: 13px; color: var(--neon-cyan); font-weight: 600">¥{{ Number(row.base_salary).toLocaleString() }}</span>
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">
              <span class="status-dot" :class="row.is_active ? 'status-online' : 'status-offline'"></span>
              {{ row.is_active ? '在职' : '离职' }}
            </el-tag>
          </div>
        </div>
      </div>

      <el-table v-else :data="list" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="100" fixed />
        <el-table-column label="角色" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="roleColor(row.role)">{{ row.role_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="team_name" label="小组" width="120" />
        <el-table-column label="负责店铺" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag v-for="(s, i) in (row.store_names || []).slice(0, 2)" :key="i" size="small" style="margin-right: 4px">{{ s }}</el-tag>
            <span v-if="(row.store_names || []).length > 2" style="color: var(--neon-cyan)">+{{ row.store_names.length - 2 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="底薪" width="100">
          <template #default="{ row }">¥{{ Number(row.base_salary).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '在职' : '离职' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="showDetail(row)" style="color: var(--neon-cyan)">详情</el-button>
            <el-button size="small" link @click="openEdit(row)" style="color: var(--neon-yellow)">编辑</el-button>
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑员工' : '新增员工'" width="650px">
      <el-tabs v-model="form.role">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="form" label-width="100px">
            <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="角色">
              <el-select v-model="form.role" style="width: 100%">
                <el-option v-for="r in roles" :key="r[0]" :label="r[1]" :value="r[0]" />
              </el-select>
            </el-form-item>
            <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="所属小组">
              <el-select v-model="form.team" style="width: 100%" clearable>
                <el-option v-for="t in teams" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="负责店铺">
              <el-select v-model="form.stores" multiple style="width: 100%" filterable placeholder="可选择多个店铺">
                <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="底薪(元)">
              <el-input-number v-model="form.base_salary" :min="0" :step="500" />
            </el-form-item>
            <el-form-item label="在职">
              <el-switch v-model="form.is_active" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane v-if="form.role === 'anchor'" label="主播档案" name="anchor">
          <el-form :model="profile" label-width="100px">
            <el-form-item label="直播昵称"><el-input v-model="profile.nickname" /></el-form-item>
            <el-form-item label="等级">
              <el-select v-model="profile.level" style="width: 100%">
                <el-option v-for="l in levels" :key="l" :label="l" :value="l" />
              </el-select>
            </el-form-item>
            <el-form-item label="风格"><el-input v-model="profile.style" /></el-form-item>
            <el-form-item label="擅长类目"><el-input v-model="profile.category_tags" /></el-form-item>
            <el-form-item label="粉丝总数"><el-input-number v-model="profile.fans_count" :min="0" /></el-form-item>
            <el-form-item label="场均观看"><el-input-number v-model="profile.avg_watch" :min="0" /></el-form-item>
            <el-form-item label="转化率(%)"><el-input-number v-model="profile.conversion_rate" :min="0" :max="100" :step="0.1" /></el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="员工详情" width="500px">
      <div v-if="detail" style="line-height: 2">
        <p><b>姓名：</b>{{ detail.name }}</p>
        <p><b>角色：</b>{{ detail.role_display }}</p>
        <p><b>电话：</b>{{ detail.phone }}</p>
        <p><b>小组：</b>{{ detail.team_name }}</p>
        <p><b>底薪：</b>¥{{ Number(detail.base_salary).toLocaleString() }}</p>
        <p><b>负责店铺：</b>
          <el-tag v-for="(s, i) in detail.store_names" :key="i" size="small" style="margin-right: 4px">{{ s }}</el-tag>
        </p>
        <div v-if="detail.anchor_profile" style="margin-top: 16px; padding: 16px; background: rgba(124, 92, 255, 0.1); border-radius: 12px; border: 1px solid var(--border-glow)">
          <h4>🎤 主播档案</h4>
          <p><b>昵称：</b>{{ detail.anchor_profile.nickname }}</p>
          <p><b>等级：</b>{{ detail.anchor_profile.level }}</p>
          <p><b>风格：</b>{{ detail.anchor_profile.style }}</p>
          <p><b>粉丝：</b>{{ detail.anchor_profile.fans_count?.toLocaleString() }}</p>
          <p><b>场均观看：</b>{{ detail.anchor_profile.avg_watch?.toLocaleString() }}</p>
          <p><b>转化率：</b>{{ detail.anchor_profile.conversion_rate }}%</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>
