<script setup>
import { ref, onMounted } from 'vue'
import { TaskAPI } from '../api'
import PageHeader from '../components/PageHeader.vue'

const boards = ref([])
const loading = ref(false)
const dialog = ref(false)
const cardDialog = ref(false)
const form = ref({})
const cardForm = ref({})
const currentBoard = ref(null)

async function load() {
  loading.value = true
  try { boards.value = await TaskAPI.list() }
  finally { loading.value = false }
}
const openBoard = (board) => { form.value = { name: '' }; currentBoard.value = null; dialog.value = true }
const saveBoard = async () => { await TaskAPI.create(form.value); dialog.value = false; load() }

const openCard = (boardId) => { cardForm.value = { board: boardId, status: 'todo', priority: 'medium' }; cardDialog.value = true }
const saveCard = async () => { await TaskAPI.createCard(cardForm.value); cardDialog.value = false; load() }
const moveCard = async (card, status) => { await TaskAPI.move(card.id, { status }); load() }

onMounted(load)
</script>

<template>
  <div class="page">
    <PageHeader title="任务看板" subtitle="团队协作 · 任务追踪 · 进度管理" />
    <div class="toolbar">
      <el-button type="primary" @click="openBoard()">+ 新建看板</el-button>
    </div>
    <div v-for="board in boards" :key="board.id" class="glass" style="padding:20px;margin-bottom:20px">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <div style="font-size:18px;font-weight:700">{{ board.name }} <span style="font-size:12px;color:var(--text-muted)">({{ board.card_count }}个任务)</span></div>
        <el-button size="small" type="primary" @click="openCard(board.id)">+ 添加任务</el-button>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px">
        <div v-for="col in ['todo','doing','done','blocked']" :key="col" style="min-height:200px">
          <div style="font-weight:600;margin-bottom:8px;padding:8px 12px;border-radius:8px;text-align:center;font-size:13px" :style="{ background: col === 'todo' ? 'rgba(168,178,209,0.15)' : col === 'doing' ? 'rgba(0,229,255,0.15)' : col === 'done' ? 'rgba(0,255,157,0.15)' : 'rgba(255,77,158,0.15)', color: col === 'todo' ? '#a8b2d1' : col === 'doing' ? '#00e5ff' : col === 'done' ? '#00ff9d' : '#ff4d9e' }">
            {{ col === 'todo' ? '待办' : col === 'doing' ? '进行中' : col === 'done' ? '已完成' : '阻塞' }}
          </div>
          <div v-for="card in board.cards.filter(c => c.status === col)" :key="card.id" style="padding:12px;margin-bottom:8px;background:rgba(255,255,255,0.03);border:1px solid var(--border-glow);border-radius:10px">
            <div style="font-weight:600;font-size:14px;margin-bottom:6px">{{ card.title }}</div>
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:8px">{{ card.assignee_name || '未分配' }} · {{ card.priority_display }}</div>
            <div style="display:flex;gap:4px;flex-wrap:wrap">
              <el-button v-if="card.status !== 'done'" size="small" @click="moveCard(card, col === 'todo' ? 'doing' : 'done')">{{ col === 'todo' ? '开始' : '完成' }}</el-button>
              <el-button v-if="card.status !== 'blocked'" size="small" type="danger" @click="moveCard(card, 'blocked')">阻塞</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <el-dialog v-model="dialog" title="新建看板" width="400px">
      <el-form :model="form" label-width="80px"><el-form-item label="看板名称"><el-input v-model="form.name" /></el-form-item></el-form>
      <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="saveBoard">创建</el-button></template>
    </el-dialog>
    <el-dialog v-model="cardDialog" title="添加任务" width="500px">
      <el-form :model="cardForm" label-width="80px">
        <el-form-item label="标题"><el-input v-model="cardForm.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="cardForm.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="优先级"><el-select v-model="cardForm.priority"><el-option label="高" value="high" /><el-option label="中" value="medium" /><el-option label="低" value="low" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="cardDialog=false">取消</el-button><el-button type="primary" @click="saveCard">创建</el-button></template>
    </el-dialog>
  </div>
</template>
