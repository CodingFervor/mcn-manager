<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">直播检查清单</text>
      <text class="page-subtitle">{{ planTitle }}</text>
    </view>

    <!-- Overall Progress -->
    <view class="glass-card progress-card">
      <view class="progress-top">
        <text class="progress-label">整体完成度</text>
        <text class="progress-value">{{ overallPercent }}%</text>
      </view>
      <view class="progress-bar">
        <view
          class="progress-fill"
          :style="{ width: overallPercent + '%' }"
          :class="{
            'fill-complete': overallPercent === 100,
          }"
        ></view>
      </view>
      <view class="progress-stats">
        <text class="stats-text">已完成 {{ completedCount }} / {{ totalCount }} 项</text>
        <text v-if="overallPercent === 100" class="stats-complete">全部完成！</text>
      </view>
    </view>

    <!-- Checklist Groups -->
    <scroll-view scroll-y class="checklist-scroll">
      <view
        v-for="(group, gi) in groups"
        :key="gi"
        class="checklist-group"
      >
        <view class="group-header">
          <view class="group-icon" :style="{ background: group.color }">
            <text class="group-icon-text">{{ group.icon }}</text>
          </view>
          <text class="group-title">{{ group.title }}</text>
          <text class="group-count">{{ getGroupCompleted(gi) }}/{{ group.items.length }}</text>
        </view>

        <view
          v-for="(item, ii) in group.items"
          :key="ii"
          class="check-item"
          :class="{ checked: item.done }"
          @tap="toggleItem(gi, ii)"
        >
          <view class="checkbox" :class="{ 'checkbox-done': item.done }">
            <text v-if="item.done" class="check-mark">&#10003;</text>
          </view>
          <view class="check-content">
            <text class="check-name" :class="{ 'name-done': item.done }">{{ item.name }}</text>
            <view v-if="item.required" class="required-tag">
              <text class="required-text">必检</text>
            </view>
          </view>
        </view>
      </view>

      <!-- Reset Button -->
      <view class="reset-section">
        <button class="btn-reset" @tap="resetAll">重置全部</button>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onPullDownRefresh } from '@dcloudio/uni-app'

const planTitle = ref('2025年6月6日 晚间直播')

const groups = ref([
  {
    title: '设备检查',
    icon: 'D',
    color: 'rgba(124,92,255,0.2)',
    items: [
      { name: '摄像头画面正常，对焦清晰', done: true, required: true },
      { name: '麦克风收音测试通过', done: true, required: true },
      { name: '补光灯角度和亮度调整', done: true, required: false },
      { name: '手机/电脑网络连接稳定', done: true, required: true },
      { name: '直播推流软件正常运行', done: false, required: true },
      { name: '备用设备准备就绪', done: false, required: false },
    ],
  },
  {
    title: '商品准备',
    icon: 'S',
    color: 'rgba(0,229,255,0.2)',
    items: [
      { name: '商品样品齐全，编号排序', done: true, required: true },
      { name: '商品价格和库存确认', done: true, required: true },
      { name: '商品链接已上架小黄车', done: false, required: true },
      { name: '优惠劵已配置并测试', done: false, required: true },
      { name: '赠品和福袋准备完毕', done: false, required: false },
    ],
  },
  {
    title: '场景布置',
    icon: 'C',
    color: 'rgba(0,255,157,0.2)',
    items: [
      { name: '直播背景整洁美观', done: true, required: true },
      { name: '品牌展示物料摆放正确', done: true, required: false },
      { name: '桌面陈列商品摆放整齐', done: false, required: true },
      { name: '灯光色调与商品匹配', done: false, required: false },
      { name: '噪音干扰排查（关闭空调等）', done: false, required: true },
    ],
  },
  {
    title: '内容准备',
    icon: 'N',
    color: 'rgba(255,210,63,0.2)',
    items: [
      { name: '直播话术脚本打印/备好', done: true, required: true },
      { name: '商品卖点卡片准备', done: true, required: true },
      { name: '互动话题和抽奖方案确认', done: false, required: false },
      { name: '敏感词规避清单查看', done: true, required: true },
      { name: '预告短视频已发布', done: true, required: false },
    ],
  },
])

const totalCount = computed(() =>
  groups.value.reduce((sum, g) => sum + g.items.length, 0)
)

const completedCount = computed(() =>
  groups.value.reduce((sum, g) => sum + g.items.filter((i) => i.done).length, 0)
)

const overallPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((completedCount.value / totalCount.value) * 100)
})

function getGroupCompleted(gi) {
  return groups.value[gi].items.filter((i) => i.done).length
}

function toggleItem(gi, ii) {
  groups.value[gi].items[ii].done = !groups.value[gi].items[ii].done

  if (overallPercent.value === 100) {
    uni.showToast({ title: '全部检查完成！可以开播了', icon: 'success' })
  }
}

function resetAll() {
  uni.showModal({
    title: '重置清单',
    content: '确定要重置所有检查项吗？',
    success(res) {
      if (res.confirm) {
        groups.value.forEach((g) => g.items.forEach((i) => (i.done = false)))
        uni.showToast({ title: '已重置', icon: 'none' })
      }
    },
  })
}

onLoad((options) => {
  if (options && options.planId) {
    // In real app, load checklist by planId
  }
})

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
  display: block;
  margin-bottom: 8rpx;
}

.page-subtitle {
  font-size: 24rpx;
  color: $text-muted;
}

.glass-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 28rpx;
  margin-bottom: 24rpx;
  backdrop-filter: blur(20px);
}

.progress-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14rpx;
}

.progress-label {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.progress-value {
  font-size: 32rpx;
  font-weight: 800;
  color: $neon-purple;
}

.progress-bar {
  height: 16rpx;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 14rpx;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  background: linear-gradient(90deg, $neon-purple, $neon-pink);
  box-shadow: 0 0 16rpx rgba($neon-purple, 0.4);
  transition: width 0.4s ease;

  &.fill-complete {
    background: linear-gradient(90deg, $neon-green, #00e5ff);
    box-shadow: 0 0 16rpx rgba($neon-green, 0.5);
  }
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-text {
  font-size: 24rpx;
  color: $text-muted;
}

.stats-complete {
  font-size: 24rpx;
  font-weight: 600;
  color: $neon-green;
  text-shadow: 0 0 12rpx rgba($neon-green, 0.5);
}

.checklist-scroll {
  height: calc(100vh - 340rpx);
}

.checklist-group {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 24rpx;
  margin-bottom: 20rpx;
  backdrop-filter: blur(20px);
}

.group-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.group-icon {
  width: 48rpx;
  height: 48rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.group-icon-text {
  font-size: 24rpx;
  font-weight: 700;
  color: $text-primary;
}

.group-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
}

.group-count {
  font-size: 24rpx;
  color: $neon-purple;
  background: rgba($neon-purple, 0.1);
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
}

.check-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.03);

  &:last-child {
    border-bottom: none;
  }

  &:active {
    opacity: 0.7;
  }

  &.checked {
    opacity: 0.7;
  }
}

.checkbox {
  width: 40rpx;
  height: 40rpx;
  border-radius: 10rpx;
  border: 2rpx solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
  transition: all 0.3s;

  &.checkbox-done {
    background: $neon-green;
    border-color: $neon-green;
    box-shadow: 0 0 12rpx rgba($neon-green, 0.4);
  }
}

.check-mark {
  font-size: 24rpx;
  font-weight: 700;
  color: $bg-primary;
}

.check-content {
  flex: 1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.check-name {
  font-size: 28rpx;
  color: $text-primary;
  line-height: 1.4;
  flex: 1;

  &.name-done {
    color: $text-muted;
    text-decoration: line-through;
  }
}

.required-tag {
  margin-left: 12rpx;
  flex-shrink: 0;
}

.required-text {
  font-size: 20rpx;
  color: $neon-pink;
  background: rgba($neon-pink, 0.12);
  border: 1rpx solid rgba($neon-pink, 0.3);
  padding: 2rpx 10rpx;
  border-radius: 6rpx;
}

.reset-section {
  padding: 20rpx 0 60rpx;
}

.btn-reset {
  background: rgba(255, 255, 255, 0.04);
  border: 1rpx solid $border-glow;
  color: $text-muted;
  font-size: 28rpx;
  border-radius: $radius-sm;
  padding: 20rpx;

  &::after {
    border: none;
  }

  &:active {
    background: rgba(255, 255, 255, 0.08);
  }
}
</style>
