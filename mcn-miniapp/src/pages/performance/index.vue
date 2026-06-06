<template>
  <view class="page">
    <view class="page-header">
      <text class="page-title">绩效考核</text>
    </view>

    <!-- Review Period -->
    <view class="glass-card period-card">
      <text class="period-label">当前考核周期</text>
      <text class="period-value">2025年 Q2 (4月-6月)</text>
      <text class="period-remain">剩余 24 天</text>
    </view>

    <!-- Score Ring -->
    <view class="glass-card score-card">
      <view class="score-ring-wrapper">
        <view class="score-ring" :style="{ background: ringConic }">
          <view class="score-ring-inner">
            <text class="score-number">{{ overallScore }}</text>
            <text class="score-unit">分</text>
          </view>
        </view>
      </view>
      <view class="score-meta">
        <view class="score-level">
          <text class="level-text" :class="'level-' + levelInfo.key">{{ levelInfo.label }}</text>
        </view>
        <text class="score-rank">团队排名: 第 {{ rank }} 名 / 共 {{ totalMembers }} 人</text>
      </view>
    </view>

    <!-- Radar Chart Placeholder -->
    <view class="glass-card radar-card">
      <view class="card-title-row">
        <text class="card-title">能力雷达图</text>
        <view class="card-underline"></view>
      </view>
      <view class="radar-wrapper">
        <view class="radar-hexagon">
          <!-- SVG radar using CSS shapes -->
          <view class="radar-bg"></view>
          <view class="radar-data" :style="{ clipPath: radarClipPath }"></view>
          <view class="radar-labels">
            <text
              v-for="(dim, i) in dimensions"
              :key="i"
              class="radar-label"
              :style="getLabelPosition(i)"
            >{{ dim.name }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- KPI Dimensions -->
    <view class="glass-card kpi-card">
      <view class="card-title-row">
        <text class="card-title">KPI 指标明细</text>
        <view class="card-underline"></view>
      </view>

      <view v-for="(dim, index) in dimensions" :key="index" class="dimension-row">
        <view class="dim-header">
          <text class="dim-name">{{ dim.name }}</text>
          <text class="dim-weight">权重 {{ dim.weight }}%</text>
        </view>
        <view class="dim-bar-row">
          <view class="dim-bar">
            <view class="dim-bar-fill" :style="{ width: dim.score + '%', background: getBarColor(dim.score) }"></view>
          </view>
          <text class="dim-score" :style="{ color: getBarColor(dim.score) }">{{ dim.score }}</text>
        </view>
        <text class="dim-desc">{{ dim.description }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onPullDownRefresh } from '@dcloudio/uni-app'

const overallScore = ref(87.5)
const rank = ref(3)
const totalMembers = ref(28)

const dimensions = ref([
  { name: '直播业绩', weight: 30, score: 92, description: 'GMV达成率、转化率、客单价' },
  { name: '粉丝增长', weight: 20, score: 85, description: '新增粉丝数、互动率、留存率' },
  { name: '内容质量', weight: 20, score: 88, description: '短视频产出、完播率、点赞收藏' },
  { name: '团队协作', weight: 15, score: 82, description: '跨部门配合、知识分享、培训参与' },
  { name: '职业素养', weight: 15, score: 90, description: '出勤率、合规性、客户满意度' },
])

const levelInfo = computed(() => {
  const s = overallScore.value
  if (s >= 95) return { label: 'S 卓越', key: 's' }
  if (s >= 85) return { label: 'A 优秀', key: 'a' }
  if (s >= 75) return { label: 'B 良好', key: 'b' }
  if (s >= 60) return { label: 'C 合格', key: 'c' }
  return { label: 'D 待改进', key: 'd' }
})

const ringConic = computed(() => {
  const percent = overallScore.value
  const deg = (percent / 100) * 360
  return `conic-gradient($neon-purple 0deg, $neon-pink ${deg}deg, rgba(255,255,255,0.06) ${deg}deg, rgba(255,255,255,0.06) 360deg)`
})

const radarClipPath = computed(() => {
  const points = dimensions.value.map((d, i) => {
    const angle = (Math.PI * 2 * i) / dimensions.value.length - Math.PI / 2
    const r = (d.score / 100) * 45
    const x = 50 + r * Math.cos(angle)
    const y = 50 + r * Math.sin(angle)
    return `${x}% ${y}%`
  })
  return `polygon(${points.join(', ')})`
})

function getLabelPosition(index) {
  const total = dimensions.value.length
  const angle = (Math.PI * 2 * index) / total - Math.PI / 2
  const r = 58
  const x = 50 + r * Math.cos(angle)
  const y = 50 + r * Math.sin(angle)
  return {
    left: `${x}%`,
    top: `${y}%`,
    transform: 'translate(-50%, -50%)',
  }
}

function getBarColor(score) {
  if (score >= 90) return '#00ff9d'
  if (score >= 80) return '#7c5cff'
  if (score >= 70) return '#00e5ff'
  if (score >= 60) return '#ffd23f'
  return '#ff4d9e'
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
  margin-bottom: 24rpx;
  padding: 0 8rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: 700;
  color: $text-primary;
}

.glass-card {
  background: $bg-card;
  border: 1rpx solid $border-glow;
  border-radius: $radius-md;
  padding: 28rpx;
  margin-bottom: 24rpx;
  backdrop-filter: blur(20px);
}

.card-title-row {
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 12rpx;
}

.card-underline {
  width: 60rpx;
  height: 4rpx;
  border-radius: 2rpx;
  background: linear-gradient(90deg, $neon-purple, $neon-pink);
  box-shadow: 0 0 10rpx rgba($neon-purple, 0.4);
}

/* Period Card */
.period-label {
  font-size: 24rpx;
  color: $text-muted;
  display: block;
  margin-bottom: 8rpx;
}

.period-value {
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
  display: block;
  margin-bottom: 8rpx;
}

.period-remain {
  font-size: 24rpx;
  color: $neon-cyan;
}

/* Score Card */
.score-card {
  display: flex;
  align-items: center;
  padding: 36rpx 28rpx;
}

.score-ring-wrapper {
  margin-right: 32rpx;
  flex-shrink: 0;
}

.score-ring {
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx;
}

.score-ring-inner {
  width: 100%;
  height: 100%;
  background: $bg-primary;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-number {
  font-size: 52rpx;
  font-weight: 800;
  color: $text-primary;
  line-height: 1;
}

.score-unit {
  font-size: 22rpx;
  color: $text-muted;
  margin-top: 4rpx;
}

.score-meta {
  flex: 1;
}

.score-level {
  margin-bottom: 16rpx;
}

.level-text {
  font-size: 36rpx;
  font-weight: 800;
  padding: 8rpx 24rpx;
  border-radius: 12rpx;
  border: 2rpx solid;
}

.level-s {
  color: $neon-yellow;
  background: rgba($neon-yellow, 0.12);
  border-color: rgba($neon-yellow, 0.4);
  text-shadow: 0 0 16rpx rgba($neon-yellow, 0.5);
}

.level-a {
  color: $neon-green;
  background: rgba($neon-green, 0.12);
  border-color: rgba($neon-green, 0.4);
  text-shadow: 0 0 16rpx rgba($neon-green, 0.5);
}

.level-b {
  color: $neon-cyan;
  background: rgba($neon-cyan, 0.12);
  border-color: rgba($neon-cyan, 0.4);
}

.level-c {
  color: $neon-purple;
  background: rgba($neon-purple, 0.12);
  border-color: rgba($neon-purple, 0.4);
}

.level-d {
  color: $neon-pink;
  background: rgba($neon-pink, 0.12);
  border-color: rgba($neon-pink, 0.4);
}

.score-rank {
  font-size: 24rpx;
  color: $text-secondary;
}

/* Radar Card */
.radar-wrapper {
  display: flex;
  justify-content: center;
  padding: 20rpx 0;
}

.radar-hexagon {
  width: 400rpx;
  height: 400rpx;
  position: relative;
}

.radar-bg {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  background: rgba(255, 255, 255, 0.04);
  clip-path: polygon(
    50% 0%, 97.6% 25%, 97.6% 75%, 50% 100%, 2.4% 75%, 2.4% 25%
  );
}

.radar-data {
  position: absolute;
  top: 10%;
  left: 10%;
  width: 80%;
  height: 80%;
  background: linear-gradient(135deg, rgba($neon-purple, 0.3), rgba($neon-pink, 0.3));
  border: 2rpx solid rgba($neon-purple, 0.6);
}

.radar-labels {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.radar-label {
  position: absolute;
  font-size: 22rpx;
  color: $text-secondary;
  white-space: nowrap;
}

/* KPI Dimensions */
.dimension-row {
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.04);

  &:last-child {
    border-bottom: none;
  }
}

.dim-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.dim-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.dim-weight {
  font-size: 22rpx;
  color: $text-muted;
}

.dim-bar-row {
  display: flex;
  align-items: center;
  margin-bottom: 8rpx;
}

.dim-bar {
  flex: 1;
  height: 14rpx;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 7rpx;
  overflow: hidden;
  margin-right: 16rpx;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 7rpx;
  transition: width 0.5s ease;
}

.dim-score {
  font-size: 28rpx;
  font-weight: 700;
  flex-shrink: 0;
  min-width: 60rpx;
  text-align: right;
}

.dim-desc {
  font-size: 22rpx;
  color: $text-muted;
}
</style>
