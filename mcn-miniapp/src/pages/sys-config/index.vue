<template>
  <view class="page">
    <view class="header">
      <text class="title">系统配置</text>
    </view>
    <scroll-view scroll-y class="scroll-body">
      <view class="group" v-for="(group, gIdx) in configGroups" :key="gIdx">
        <view class="group-header">
          <text class="group-title">{{ group.name }}</text>
          <view class="btn-save-sm" @tap="saveGroup(gIdx)">
            <text class="save-sm-text">保存</text>
          </view>
        </view>
        <view class="card">
          <view class="field" v-for="(item, idx) in group.items" :key="idx">
            <view class="field-top">
              <text class="field-key">{{ item.key }}</text>
            </view>
            <input
              class="field-input"
              :value="item.value"
              @input="onInput(gIdx, idx, $event)"
              :placeholder="item.description"
            />
            <text class="field-desc">{{ item.description }}</text>
          </view>
        </view>
      </view>
      <view class="bottom-spacer" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const configGroups = ref([
  {
    name: '基础设置',
    items: [
      { key: 'app.name', value: 'MCN管家', description: '应用名称' },
      { key: 'app.version', value: '3.2.0', description: '当前版本号' },
      { key: 'app.locale', value: 'zh-CN', description: '默认语言' },
    ],
  },
  {
    name: '邮件服务',
    items: [
      { key: 'mail.smtp_host', value: 'smtp.example.com', description: 'SMTP服务器地址' },
      { key: 'mail.smtp_port', value: '465', description: 'SMTP端口' },
      { key: 'mail.from_address', value: 'noreply@mcnguanjia.com', description: '发件人地址' },
    ],
  },
  {
    name: '存储配置',
    items: [
      { key: 'storage.driver', value: 'oss', description: '存储驱动 (oss/s3/local)' },
      { key: 'storage.bucket', value: 'mcn-prod', description: '存储桶名称' },
      { key: 'storage.max_size', value: '50MB', description: '单文件最大大小' },
    ],
  },
  {
    name: '安全设置',
    items: [
      { key: 'security.jwt_ttl', value: '7200', description: 'JWT有效期(秒)' },
      { key: 'security.rate_limit', value: '100', description: 'API每分钟限流次数' },
      { key: 'security.password_min', value: '8', description: '密码最小长度' },
    ],
  },
])

function onInput(gIdx, idx, e) {
  configGroups.value[gIdx].items[idx].value = e.detail.value
}

function saveGroup(gIdx) {
  uni.showToast({ title: '已保存 ' + configGroups.value[gIdx].name, icon: 'success' })
}
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

.group {
  margin-bottom: 8rpx;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 8rpx 8rpx;
}

.group-title {
  font-size: 26rpx;
  font-weight: 600;
  color: $neon-purple;
}

.btn-save-sm {
  padding: 6rpx 20rpx;
  background: rgba(124, 92, 255, 0.15);
  border: 1rpx solid rgba(124, 92, 255, 0.3);
  border-radius: 20rpx;
}

.save-sm-text {
  font-size: 22rpx;
  color: $neon-purple;
  font-weight: 500;
}

.card {
  padding: 24rpx 28rpx;
  background: $bg-card;
  border-radius: $radius-md;
  border: 1rpx solid $border-glow;
  margin-bottom: 16rpx;
}

.field {
  padding: 16rpx 0;
  border-bottom: 1rpx solid rgba(124, 92, 255, 0.06);

  &:last-child { border-bottom: none; }
}

.field-top {
  margin-bottom: 8rpx;
}

.field-key {
  font-size: 24rpx;
  font-weight: 600;
  color: $neon-cyan;
  font-family: monospace;
}

.field-input {
  padding: 14rpx 20rpx;
  background: rgba(10, 14, 39, 0.6);
  border: 1rpx solid rgba(124, 92, 255, 0.15);
  border-radius: $radius-sm;
  font-size: 26rpx;
  color: $text-primary;
  margin-bottom: 6rpx;
}

.field-desc {
  font-size: 22rpx;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
