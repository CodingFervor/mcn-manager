<template>
  <view class="page">
    <view class="header">
      <text class="title">风险评估</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <!-- Stats -->
      <view class="stats-row">
        <view class="stat-chip" v-for="(s, si) in riskStats" :key="si">
          <view class="stat-dot" :style="{ background: s.color }" />
          <text class="stat-num">{{ s.count }}</text>
          <text class="stat-lbl">{{ s.label }}</text>
        </view>
      </view>
      <!-- Risk Matrix -->
      <view class="matrix-section">
        <text class="section-title">风险矩阵</text>
        <view class="matrix">
          <view class="matrix-row" v-for="(row, ri) in matrix" :key="ri">
            <text class="matrix-label">{{ row.label }}</text>
            <view class="matrix-cell" v-for="(cell, ci) in row.cells" :key="ci" :class="'level-' + cell.level">
              <text class="cell-count">{{ cell.count }}</text>
            </view>
          </view>
        </view>
        <view class="matrix-axis">
          <text class="axis-label">低概率</text>
          <text class="axis-label">高概率</text>
        </view>
      </view>
      <!-- Risk List -->
      <view class="card" v-for="(item, idx) in risks" :key="idx">
        <view class="card-top">
          <text class="card-name">{{ item.name }}</text>
          <view class="severity-tag" :class="'sev-' + item.severity">
            <text class="sev-text">{{ item.severityLabel }}</text>
          </view>
        </view>
        <text class="card-desc">{{ item.description }}</text>
        <view class="card-bottom">
          <text class="card-category">{{ item.category }}</text>
          <text class="card-owner">负责人: {{ item.owner }}</text>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const riskStats = [
  { label: '总计', count: 18, color: '#a8b2d1' },
  { label: '低', count: 8, color: '#00ff9d' },
  { label: '中', count: 6, color: '#ffd23f' },
  { label: '高', count: 3, color: '#ff8c42' },
  { label: '严重', count: 1, color: '#ff4d9e' },
]

const matrix = [
  { label: '高严重', cells: [{ level: 'med', count: 1 }, { level: 'high', count: 1 }, { level: 'crit', count: 1 }] },
  { label: '中严重', cells: [{ level: 'low', count: 2 }, { level: 'med', count: 2 }, { level: 'high', count: 1 }] },
  { label: '低严重', cells: [{ level: 'low', count: 4 }, { level: 'low', count: 3 }, { level: 'med', count: 3 }] },
]

const risks = ref([
  { name: '数据库单点故障', severity: 'critical', severityLabel: '严重', description: '主数据库无高可用备份，存在单点故障风险', category: '基础设施', owner: '运维团队' },
  { name: '敏感数据泄露', severity: 'high', severityLabel: '高', description: '部分API接口缺少数据脱敏处理', category: '信息安全', owner: '安全团队' },
  { name: '第三方服务依赖', severity: 'high', severityLabel: '高', description: '核心支付链路依赖单一第三方通道', category: '业务风险', owner: '技术团队' },
  { name: 'SSL证书过期', severity: 'high', severityLabel: '高', description: '多域名证书将于近期集中过期', category: '基础设施', owner: '运维团队' },
  { name: '代码审查覆盖不足', severity: 'medium', severityLabel: '中', description: '代码审查覆盖率仅为60%', category: '开发流程', owner: '研发团队' },
  { name: '日志存储空间不足', severity: 'medium', severityLabel: '中', description: '日志存储空间使用率已达80%', category: '基础设施', owner: '运维团队' },
  { name: '文档更新滞后', severity: 'low', severityLabel: '低', description: 'API文档与实际接口存在偏差', category: '开发流程', owner: '研发团队' },
])
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 24rpx 32rpx 16rpx;
}

.title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
}

.scroll-body {
  flex: 1;
  height: 0;
  padding: 0 24rpx;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  padding: 20rpx 16rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 20rpx;
}

.stat-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.stat-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin-bottom: 4rpx;
}

.stat-num {
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.stat-lbl {
  font-size: 20rpx;
  color: $text-muted;
}

.matrix-section {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 20rpx;
  display: block;
}

.matrix {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.matrix-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.matrix-label {
  font-size: 22rpx;
  color: $text-muted;
  min-width: 80rpx;
}

.matrix-cell {
  flex: 1;
  height: 64rpx;
  border-radius: $radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;

  &.level-low { background: rgba(0, 255, 157, 0.12); }
  &.level-med { background: rgba(255, 210, 63, 0.15); }
  &.level-high { background: rgba(255, 140, 66, 0.15); }
  &.level-crit { background: rgba(255, 77, 158, 0.2); }
}

.cell-count {
  font-size: 24rpx;
  font-weight: 600;
  color: $text-primary;
}

.matrix-axis {
  display: flex;
  justify-content: space-between;
  padding: 8rpx 80rpx 0;
}

.axis-label {
  font-size: 20rpx;
  color: $text-muted;
}

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
}

.severity-tag {
  padding: 4rpx 14rpx;
  border-radius: 8rpx;

  &.sev-low { background: rgba(0, 255, 157, 0.12); }
  &.sev-medium { background: rgba(255, 210, 63, 0.12); }
  &.sev-high { background: rgba(255, 140, 66, 0.12); }
  &.sev-critical { background: rgba(255, 77, 158, 0.15); }
}

.sev-text {
  font-size: 22rpx;
  font-weight: 600;
  .sev-low & { color: $neon-green; }
  .sev-medium & { color: $neon-yellow; }
  .sev-high & { color: #ff8c42; }
  .sev-critical & { color: $neon-pink; }
}

.card-desc {
  font-size: 24rpx;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: 12rpx;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
}

.card-category {
  font-size: 22rpx;
  color: $neon-cyan;
}

.card-owner {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
