<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ShiftAPI } from '../api'
import { Plus, Clock, Sunny, Moon, Sunrise, Sunset, EditPen, Delete } from '@element-plus/icons-vue'

const list = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = ref({ name: '', type: 'morning', start_time: '08:00:00', end_time: '12:00:00', color: '#7c5cff', description: '', late_minutes: 10 })
const editingId = ref(null)

const types = [
  { v: 'morning', l: '☀ 早班', icon: Sunrise, grad: 'g3' },
  { v: 'afternoon', l: '🌤 中班', icon: Sunny, grad: 'g5' },
  { v: 'evening', l: '🌆 晚班', icon: Sunset, grad: 'g1' },
  { v: 'night', l: '🌙 夜班', icon: Moon, grad: 'g4' },
  { v: 'custom', l: '⚡ 自定义', icon: Clock, grad: 'g2' }
]
const colors = ['#7c5cff', '#ff4d9e', '#00e5ff', '#00ff9d', '#ffd23f', '#fa541c', '#13c2c2']

const load = async () => {
  loading.value = true
  try { list.value = await ShiftAPI.list() } finally { loading.value = false }
}

const openCreate = () => {
  editingId.value = null
  form.value = { name: '', type: 'morning', start_time: '08:00:00', end_time: '12:00:00', color: '#7c5cff', description: '', late_minutes: 10 }
  dialogVisible.value = true
}
const openEdit = (row) => {
  editingId.value = row.id
  form.value = { ...row }
  dialogVisible.value = true
}
const submit = async () => {
  if (editingId.value) await ShiftAPI.update(editingId.value, form.value)
  else await ShiftAPI.create(form.value)
  ElMessage.success('✨ 保存成功')
  dialogVisible.value = false
  load()
}
const remove = async (row) => {
  await ElMessageBox.confirm(`确定删除班次「${row.name}」？`, '提示', { type: 'warning' })
  await ShiftAPI.remove(row.id)
  ElMessage.success('已删除')
  load()
}

const typeMeta = (v) => types.find(t => t.v === v) || types[4]
const fmtTime = (t) => t?.slice(0, 5) || '--:--'

onMounted(load)
</script>

<template>
  <div class="page" v-loading="loading">
    <h1 class="page-title animate-slide">班次配置 <span class="live-dot" style="margin-left: 8px"></span></h1>
    <div class="page-subtitle">灵活配置早晚班次 · 自定义时段 · 迟到容忍阈值</div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col :span="6">
        <div class="stat-card g1"><el-icon class="stat-icon"><Clock /></el-icon>
          <div class="stat-label">班次总数</div>
          <div class="stat-value">{{ list.length }}</div>
          <div class="stat-trend">⏰ 时段</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g3"><el-icon class="stat-icon"><Sunrise /></el-icon>
          <div class="stat-label">早班</div>
          <div class="stat-value">{{ list.filter(s => s.type === 'morning').length }}</div>
          <div class="stat-trend">☀ 08-12点</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g4"><el-icon class="stat-icon"><Moon /></el-icon>
          <div class="stat-label">夜班</div>
          <div class="stat-value">{{ list.filter(s => s.type === 'night').length }}</div>
          <div class="stat-trend">🌙 凌晨档</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card g2"><el-icon class="stat-icon"><Sunset /></el-icon>
          <div class="stat-label">自定义</div>
          <div class="stat-value">{{ list.filter(s => s.type === 'custom').length }}</div>
          <div class="stat-trend">⚡ 灵活</div>
        </div>
      </el-col>
    </el-row>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; margin-bottom: 16px">
      <div v-for="row in list" :key="row.id" class="glass" style="padding: 20px; position: relative; overflow: hidden; cursor: pointer" @click="openEdit(row)">
        <div :style="`position: absolute; top: 0; right: 0; width: 120px; height: 120px; background: radial-gradient(circle, ${row.color}40, transparent 70%); pointer-events: none`"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px; position: relative">
          <div :class="`stat-card ${typeMeta(row.type).grad}`" style="width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; padding: 0; flex-shrink: 0">
            <el-icon :size="24"><component :is="typeMeta(row.type).icon" /></el-icon>
          </div>
          <div style="flex: 1; min-width: 0">
            <div style="font-weight: 800; color: white; font-size: 17px">{{ row.name }}</div>
            <el-tag size="small" effect="dark" :color="row.color" style="color: white; border: none; margin-top: 4px">
              {{ row.type_display }}
            </el-tag>
          </div>
        </div>

        <div style="display: flex; align-items: center; gap: 8px; padding: 14px; background: rgba(255, 255, 255, 0.03); border-radius: 12px; margin-bottom: 12px; position: relative">
          <div style="text-align: center; flex: 1">
            <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px">开 始</div>
            <div style="font-size: 22px; font-weight: 800; color: var(--neon-cyan); font-family: 'Courier New', monospace">
              {{ fmtTime(row.start_time) }}
            </div>
          </div>
          <div style="color: var(--neon-pink); font-size: 18px">→</div>
          <div style="text-align: center; flex: 1">
            <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px">结 束</div>
            <div style="font-size: 22px; font-weight: 800; color: var(--neon-pink); font-family: 'Courier New', monospace">
              {{ fmtTime(row.end_time) }}
            </div>
          </div>
        </div>

        <div v-if="row.description" style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; padding: 8px 12px; background: rgba(124, 92, 255, 0.08); border-radius: 8px; border-left: 3px solid var(--neon-purple)">
          {{ row.description }}
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid var(--border-glow); position: relative">
          <div style="display: flex; align-items: center; gap: 6px">
            <el-icon style="color: var(--neon-yellow)"><Clock /></el-icon>
            <span style="font-size: 12px; color: var(--text-muted)">迟到容忍</span>
            <el-tag size="small" effect="dark" type="warning">{{ row.late_minutes }}分</el-tag>
          </div>
          <el-button-group>
            <el-button size="small" link @click.stop="openEdit(row)" style="color: var(--neon-cyan)">
              <el-icon><EditPen /></el-icon>
            </el-button>
            <el-button size="small" link type="danger" @click.stop="remove(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <el-card>
      <div class="toolbar">
        <span style="font-weight: 700; color: var(--neon-cyan)">📋 详细列表</span>
        <div style="flex: 1"></div>
        <el-button type="primary" @click="openCreate" style="background: var(--grad-1)">
          <el-icon><Plus /></el-icon><span style="margin-left: 4px">新增班次</span>
        </el-button>
      </div>
      <el-table :data="list" stripe size="small">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="班次" width="160">
          <template #default="{ row }">
            <el-tag :color="row.color" style="color: white; border: none; font-weight: 600; padding: 6px 12px; border-radius: 10px">
              {{ row.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="dark" :color="row.color" style="color: white; border: none">
              {{ row.type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="时段" width="180">
          <template #default="{ row }">
            <span style="font-family: 'Courier New', monospace; color: var(--neon-cyan); font-weight: 700">{{ fmtTime(row.start_time) }}</span>
            <span style="color: var(--text-muted); margin: 0 6px">→</span>
            <span style="font-family: 'Courier New', monospace; color: var(--neon-pink); font-weight: 700">{{ fmtTime(row.end_time) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="迟到容忍" width="110">
          <template #default="{ row }">
            <el-tag size="small" effect="dark" type="warning">{{ row.late_minutes }} 分钟</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" link @click="openEdit(row)" style="color: var(--neon-cyan)">
              <el-icon><EditPen /></el-icon><span style="margin-left: 2px">编辑</span>
            </el-button>
            <el-button size="small" link type="danger" @click="remove(row)">
              <el-icon><Delete /></el-icon><span style="margin-left: 2px">删除</span>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editingId ? '✏️ 编辑班次' : '✨ 新增班次'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="如：晚间黄金档" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option v-for="t in types" :key="t.v" :label="t.l" :value="t.v" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm:ss" style="width: 100%" />
        </el-form-item>
        <el-form-item label="主题色">
          <el-select v-model="form.color" style="width: 100%">
            <el-option v-for="c in colors" :key="c" :value="c">
              <div style="display: flex; align-items: center; gap: 8px">
                <span :style="{background:c,display:'inline-block',width:'24px',height:'24px',borderRadius:'6px',boxShadow:`0 0 12px ${c}80`}"></span>
                <span :style="{color:c,fontWeight:600}">{{ c }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="迟到容忍(分)">
          <el-input-number v-model="form.late_minutes" :min="0" :max="60" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="班次说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submit" style="background: var(--grad-1)">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
