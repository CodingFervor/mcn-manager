<template>
  <view class="page">
    <!-- Search Bar -->
    <view class="search-bar">
      <view class="search-input-wrap">
        <text class="search-icon">&#128269;</text>
        <input
          class="search-input"
          v-model="keyword"
          placeholder="搜索文档标题"
          placeholder-class="search-placeholder"
          confirm-type="search"
          @confirm="onSearch"
        />
      </view>
    </view>

    <!-- Category Filter Tabs -->
    <scroll-view scroll-x class="category-scroll">
      <view class="category-tabs">
        <view
          v-for="cat in categories"
          :key="cat"
          :class="['cat-tab', { active: activeCategory === cat }]"
          @tap="activeCategory = cat"
        >
          <text class="cat-text">{{ cat }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Document List -->
    <scroll-view scroll-y class="doc-list">
      <view
        v-for="doc in filteredDocs"
        :key="doc.id"
        class="glass-card doc-card"
        @tap="goDetail(doc.id)"
      >
        <view class="doc-top">
          <text class="doc-title">{{ doc.title }}</text>
          <text :class="['doc-tag', `tag-${doc.category}`]">{{ doc.category }}</text>
        </view>
        <view class="doc-meta">
          <text class="meta-author">{{ doc.author }}</text>
          <text class="meta-date">更新于 {{ formatDate(doc.updatedAt) }}</text>
        </view>
      </view>

      <view v-if="filteredDocs.length === 0" class="empty-tip">
        <text class="tip-text">暂无文档</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh } from '@dcloudio/uni-app'
import { KnowledgeAPI } from '@/api'
import { formatDate } from '@/utils/format'

const keyword = ref('')
const activeCategory = ref('全部')
const documents = ref([])

const categories = ['全部', '直播话术', '运营规范', '产品知识', '培训资料', '公司制度']

const mockDocuments = [
  { id: 1, title: '618大促直播话术指南', category: '直播话术', author: '张小明', updatedAt: '2026-06-05' },
  { id: 2, title: '护肤品类专业话术手册', category: '直播话术', author: '赵丽丽', updatedAt: '2026-06-03' },
  { id: 3, title: '彩妆产品介绍模板', category: '直播话术', author: '张小明', updatedAt: '2026-05-28' },
  { id: 4, title: '直播间互动技巧汇总', category: '直播话术', author: '赵丽丽', updatedAt: '2026-05-25' },
  { id: 5, title: '直播间运营标准流程', category: '运营规范', author: '李思思', updatedAt: '2026-06-01' },
  { id: 6, title: '直播前后检查清单规范', category: '运营规范', author: '李思思', updatedAt: '2026-05-30' },
  { id: 7, title: '粉丝社群运营指南', category: '运营规范', author: '王大伟', updatedAt: '2026-05-20' },
  { id: 8, title: '玻尿酸系列成分解析', category: '产品知识', author: '李思思', updatedAt: '2026-06-04' },
  { id: 9, title: '防晒产品选购指南', category: '产品知识', author: '赵丽丽', updatedAt: '2026-06-02' },
  { id: 10, title: '新品上市产品手册v2.0', category: '产品知识', author: '王大伟', updatedAt: '2026-05-29' },
  { id: 11, title: '新主播入职培训手册', category: '培训资料', author: '张小明', updatedAt: '2026-05-27' },
  { id: 12, title: '直播数据分析入门', category: '培训资料', author: '李思思', updatedAt: '2026-05-22' },
  { id: 13, title: '短视频拍摄基础教程', category: '培训资料', author: '王大伟', updatedAt: '2026-05-18' },
  { id: 14, title: '员工考勤管理制度', category: '公司制度', author: '人事部', updatedAt: '2026-04-01' },
  { id: 15, title: '直播提成计算方案', category: '公司制度', author: '财务部', updatedAt: '2026-03-15' }
]

const filteredDocs = computed(() => {
  let list = documents.value
  if (activeCategory.value !== '全部') {
    list = list.filter(d => d.category === activeCategory.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter(d => d.title.toLowerCase().includes(kw))
  }
  return list
})

function onSearch() {
  // keyword is reactive, filteredDocs auto updates
}

function goDetail(id) {
  uni.navigateTo({ url: `/pages/knowledge/detail?id=${id}` })
}

async function loadData() {
  try {
    const res = await KnowledgeAPI.list()
    documents.value = res.data?.results || res.data || mockDocuments
  } catch {
    documents.value = mockDocuments
  }
}

onShow(() => {
  loadData()
})

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
}

.search-bar {
  padding: 24rpx 32rpx 12rpx;
}

.search-input-wrap {
  display: flex;
  align-items: center;
  background: $bg-secondary;
  border: 2rpx solid $border-glow;
  border-radius: $radius-sm;
  padding: 16rpx 24rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: $text-primary;
}

.search-placeholder {
  color: $text-muted;
}

.category-scroll {
  padding: 0 32rpx;
  margin-bottom: 16rpx;
  white-space: nowrap;
}

.category-tabs {
  display: flex;
  gap: 16rpx;
}

.cat-tab {
  padding: 12rpx 28rpx;
  border-radius: $radius-sm;
  background: $bg-secondary;
  border: 2rpx solid transparent;
  flex-shrink: 0;

  &.active {
    background: rgba($neon-purple, 0.15);
    border-color: $neon-purple;
  }
}

.cat-text {
  font-size: 26rpx;
  color: $text-secondary;

  .active & {
    color: $neon-purple;
    font-weight: 600;
  }
}

.doc-list {
  padding: 0 32rpx;
  height: calc(100vh - 260rpx);
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.doc-card {
  padding: 24rpx 28rpx;
  margin-bottom: 16rpx;
}

.doc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12rpx;
}

.doc-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
  margin-right: 16rpx;
  line-height: 1.4;
}

.doc-tag {
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  flex-shrink: 0;

  &.tag-直播话术 { background: rgba($neon-purple, 0.15); color: $neon-purple; }
  &.tag-运营规范 { background: rgba($neon-cyan, 0.15); color: $neon-cyan; }
  &.tag-产品知识 { background: rgba($neon-green, 0.15); color: $neon-green; }
  &.tag-培训资料 { background: rgba($neon-yellow, 0.15); color: $neon-yellow; }
  &.tag-公司制度 { background: rgba($neon-pink, 0.15); color: $neon-pink; }
}

.doc-meta {
  display: flex;
  gap: 24rpx;
}

.meta-author {
  font-size: 24rpx;
  color: $text-secondary;
}

.meta-date {
  font-size: 24rpx;
  color: $text-muted;
}

.empty-tip {
  padding: 80rpx 0;
  text-align: center;
}

.tip-text {
  font-size: 28rpx;
  color: $text-muted;
}
</style>
