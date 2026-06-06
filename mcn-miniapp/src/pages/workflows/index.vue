<template>
  <view class="page">
    <view class="header">
      <text class="title">工作流模板</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="card" v-for="(item, idx) in workflows" :key="idx">
        <view class="card-top">
          <view class="card-left">
            <text class="card-name">{{ item.name }}</text>
            <view class="trigger-tag">
              <text class="trigger-text">{{ item.trigger }}</text>
            </view>
          </view>
          <view class="switch-wrap" @tap="item.active = !item.active">
            <view class="switch-track" :class="{ on: item.active }">
              <view class="switch-thumb" />
            </view>
          </view>
        </view>
        <view class="steps-label">
          <text class="steps-count">{{ item.steps.length }} 个步骤</text>
        </view>
        <view class="timeline">
          <view class="timeline-item" v-for="(step, si) in item.steps" :key="si">
            <view class="tl-line-wrap">
              <view class="tl-dot" :class="{ 'dot-active': item.active }" />
              <view v-if="si < item.steps.length - 1" class="tl-line" />
            </view>
            <view class="tl-content">
              <text class="tl-name">{{ step.name }}</text>
              <text class="tl-desc">{{ step.desc }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const workflows = ref([
  {
    name: '订单审批流', trigger: '自动触发', active: true,
    steps: [
      { name: '接收订单', desc: '系统自动接收新订单' },
      { name: '风控检查', desc: '自动检测异常订单' },
      { name: '主管审批', desc: '大额订单需主管确认' },
      { name: '发货通知', desc: '审批通过后通知仓库' },
    ],
  },
  {
    name: '退款处理流', trigger: '用户申请', active: true,
    steps: [
      { name: '用户申请', desc: '提交退款申请' },
      { name: '客服初审', desc: '核实退款原因' },
      { name: '财务审核', desc: '确认退款金额' },
      { name: '执行退款', desc: '原路退回款项' },
    ],
  },
  {
    name: '内容发布流', trigger: '定时触发', active: false,
    steps: [
      { name: '内容编辑', desc: '编辑完成待审核' },
      { name: 'AI审核', desc: '智能内容合规检测' },
      { name: '人工复核', desc: '运营人员最终确认' },
      { name: '定时发布', desc: '按计划时间发布' },
    ],
  },
  {
    name: '员工入职流', trigger: '手动触发', active: true,
    steps: [
      { name: 'HR录入', desc: '填写员工基本信息' },
      { name: '部门分配', desc: '分配所属部门和岗位' },
      { name: '账号开通', desc: '自动创建系统账号' },
      { name: '培训安排', desc: '生成培训计划' },
    ],
  },
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

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 20rpx;
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.card-name {
  font-size: 28rpx;
  font-weight: 600;
  color: $text-primary;
}

.trigger-tag {
  padding: 2rpx 12rpx;
  border-radius: 8rpx;
  background: rgba(124, 92, 255, 0.12);
}

.trigger-text {
  font-size: 20rpx;
  color: $neon-purple;
}

.switch-track {
  width: 76rpx;
  height: 42rpx;
  border-radius: 21rpx;
  background: rgba(107, 115, 147, 0.3);
  position: relative;

  &.on { background: rgba(124, 92, 255, 0.5); }
}

.switch-thumb {
  width: 34rpx;
  height: 34rpx;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  transition: transform 0.3s;

  .on & { transform: translateX(34rpx); }
}

.steps-label {
  margin-bottom: 16rpx;
}

.steps-count {
  font-size: 24rpx;
  color: $text-muted;
}

.timeline {
  display: flex;
  flex-direction: column;
}

.timeline-item {
  display: flex;
  min-height: 80rpx;
}

.tl-line-wrap {
  width: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.tl-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  background: $text-muted;
  flex-shrink: 0;
  margin-top: 6rpx;

  &.dot-active {
    background: $neon-purple;
    box-shadow: 0 0 10rpx rgba(124, 92, 255, 0.4);
  }
}

.tl-line {
  width: 2rpx;
  flex: 1;
  background: rgba(124, 92, 255, 0.2);
  margin: 4rpx 0;
}

.tl-content {
  flex: 1;
  padding-left: 16rpx 0 16rpx;
  padding-bottom: 16rpx;
}

.tl-name {
  font-size: 26rpx;
  font-weight: 500;
  color: $text-primary;
  display: block;
  margin-bottom: 4rpx;
}

.tl-desc {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
