<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">培训课程</text>
    </view>

    <scroll-view scroll-x class="filter-tabs">
      <view
        v-for="tab in tabs"
        :key="tab.key"
        class="filter-tab"
        :class="{ active: activeTab === tab.key }"
        @tap="activeTab = tab.key"
      >
        <text class="filter-tab-text" :class="{ 'active-text': activeTab === tab.key }">
          {{ tab.label }}
        </text>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="course-list">
      <view
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
        @tap="openCourse(course)"
      >
        <view class="course-header">
          <view class="course-category" :style="{ background: course.categoryColor }">
            <text class="category-text">{{ course.category }}</text>
          </view>
          <text class="course-status" :class="'status-' + course.status">{{ course.statusText }}</text>
        </view>
        <text class="course-title">{{ course.title }}</text>
        <view class="course-meta">
          <text class="meta-item">{{ course.duration }}</text>
          <text class="meta-divider">|</text>
          <text class="meta-item">{{ course.instructor }}</text>
          <text class="meta-divider">|</text>
          <text class="meta-item">{{ course.lessons }} 课时</text>
        </view>
        <view class="progress-section">
          <view class="progress-info">
            <text class="progress-label">学习进度</text>
            <text class="progress-value">{{ course.progress }}%</text>
          </view>
          <view class="progress-bar">
            <view
              class="progress-fill"
              :style="{ width: course.progress + '%', background: course.progress === 100 ? $neonGreen : undefined }"
            ></view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'ongoing', label: '进行中' },
  { key: 'completed', label: '已完成' },
]

const activeTab = ref('all')

const courses = ref([
  {
    id: 1,
    title: '直播间话术技巧与转化策略',
    category: '直播运营',
    categoryColor: 'rgba(124,92,255,0.2)',
    duration: '3小时',
    instructor: '王老师',
    lessons: 12,
    progress: 75,
    status: 'ongoing',
    statusText: '进行中',
  },
  {
    id: 2,
    title: '短视频拍摄与剪辑实战',
    category: '内容创作',
    categoryBackground: 'rgba(0,229,255,0.2)',
    categoryColor: 'rgba(0,229,255,0.2)',
    duration: '5小时',
    instructor: '李导演',
    lessons: 20,
    progress: 40,
    status: 'ongoing',
    statusText: '进行中',
  },
  {
    id: 3,
    title: 'MCN行业规范与合规培训',
    category: '合规培训',
    categoryColor: 'rgba(255,77,158,0.2)',
    duration: '2小时',
    instructor: '法务部',
    lessons: 8,
    progress: 100,
    status: 'completed',
    statusText: '已完成',
  },
  {
    id: 4,
    title: '电商数据分析基础',
    category: '数据分析',
    categoryColor: 'rgba(0,255,157,0.2)',
    duration: '4小时',
    instructor: '陈数据',
    lessons: 16,
    progress: 100,
    status: 'completed',
    statusText: '已完成',
  },
  {
    id: 5,
    title: '客户服务与售后处理规范',
    category: '客服技能',
    categoryColor: 'rgba(255,210,63,0.2)',
    duration: '2.5小时',
    instructor: '客服主管',
    lessons: 10,
    progress: 20,
    status: 'ongoing',
    statusText: '进行中',
  },
  {
    id: 6,
    title: '新品选品与供应链管理',
    category: '选品运营',
    categoryColor: 'rgba(124,92,255,0.2)',
    duration: '3.5小时',
    instructor: '张采购',
    lessons: 14,
    progress: 0,
    status: 'ongoing',
    statusText: '未开始',
  },
  {
    id: 7,
    title: '个人IP打造与粉丝运营',
    category: '内容创作',
    categoryColor: 'rgba(0,229,255,0.2)',
    duration: '4小时',
    instructor: '赵大V',
    lessons: 18,
    progress: 60,
    status: 'ongoing',
    statusText: '进行中',
  },
])

const filteredCourses = computed(() => {
  if (activeTab.value === 'all') return courses.value
  if (activeTab.value === 'ongoing') return courses.value.filter((c) => c.status === 'ongoing')
  if (activeTab.value === 'completed') return courses.value.filter((c) => c.status === 'completed')
  return courses.value
})

function openCourse(course) {
  uni.showToast({ title: course.title, icon: 'none' })
}

onPullDownRefresh(() => {
  setTimeout(() => {
    uni.stopPullDownRefresh()
  }, 1000)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 20rpx 24rpx;
}

.page-header {
  margin-bottom: 20rpx;
  padding: 0 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
}

.filter-tabs {
  white-space: nowrap;
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.filter-tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12rpx 32rpx;
  border-radius: 40rpx;
  background: $bg-card;
  border: 1rpx solid $border-glow;
  margin-right: 16rpx;
  transition: all 0.3s;

  &.active {
    background: rgba($neon-purple, 0.25);
    border-color: $neon-purple;
    box-shadow: 0 0 20rpx rgba($neon-purple, 0.3);
  }
}

.filter-tab-text {
  font-size: 26rpx;
  color: $text-secondary;

  &.active-text {
    color: $text-primary;
    font-weight: 600;
  }
}

.course-list {
  height: calc(100vh - 220rpx);
}

.course-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 28rpx;
  margin-bottom: 20rpx;
  backdrop-filter: blur(20px);

  &:active {
    border-color: rgba($neon-purple, 0.6);
  }
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.course-category {
  border-radius: 8rpx;
  padding: 4rpx 16rpx;
}

.category-text {
  font-size: 22rpx;
  color: $text-primary;
}

.course-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;

  &.status-ongoing {
    color: $neon-cyan;
    background: rgba($neon-cyan, 0.12);
    border: 1rpx solid rgba($neon-cyan, 0.3);
  }

  &.status-completed {
    color: $neon-green;
    background: rgba($neon-green, 0.12);
    border: 1rpx solid rgba($neon-green, 0.3);
  }
}

.course-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 12rpx;
  line-height: 1.4;
}

.course-meta {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.meta-item {
  font-size: 22rpx;
  color: $text-muted;
}

.meta-divider {
  font-size: 22rpx;
  color: $text-muted;
  margin: 0 12rpx;
}

.progress-section {
  margin-top: 8rpx;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10rpx;
}

.progress-label {
  font-size: 22rpx;
  color: $text-secondary;
}

.progress-value {
  font-size: 22rpx;
  color: $neon-purple;
  font-weight: 600;
}

.progress-bar {
  height: 12rpx;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 6rpx;
  background: linear-gradient(90deg, $neon-purple, $neon-pink);
  box-shadow: 0 0 12rpx rgba($neon-purple, 0.4);
  transition: width 0.5s ease;
}
</style>
