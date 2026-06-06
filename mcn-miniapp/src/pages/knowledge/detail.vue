<template>
  <view class="page">
    <!-- Header -->
    <view class="glass-card header-card">
      <text class="doc-title">{{ document.title }}</text>
      <view class="meta-row">
        <text class="meta-item">作者: {{ document.author }}</text>
        <text class="meta-item">{{ formatDate(document.updatedAt) }}</text>
      </view>
      <text :class="['doc-tag', `tag-${document.category}`]">{{ document.category }}</text>
    </view>

    <!-- Content -->
    <scroll-view scroll-y class="content-scroll">
      <view class="glass-card content-card">
        <view class="content-block">
          <text class="block-title">概述</text>
          <text class="block-text">{{ document.summary }}</text>
        </view>

        <view v-for="(section, idx) in document.sections" :key="idx" class="content-block">
          <text class="block-title">{{ section.heading }}</text>
          <text
            v-for="(para, pIdx) in section.paragraphs"
            :key="pIdx"
            class="block-text"
          >{{ para }}</text>
          <view v-if="section.listItems && section.listItems.length" class="block-list">
            <view
              v-for="(li, liIdx) in section.listItems"
              :key="liIdx"
              class="list-item"
            >
              <view class="list-dot"></view>
              <text class="list-text">{{ li }}</text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-spacer"></view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { KnowledgeAPI } from '@/api'
import { formatDate } from '@/utils/format'

const docId = ref('')
const document = ref({
  title: '',
  author: '',
  updatedAt: '',
  category: '',
  summary: '',
  sections: []
})

const mockDocs = {
  '1': {
    title: '618大促直播话术指南',
    author: '张小明',
    updatedAt: '2026-06-05',
    category: '直播话术',
    summary: '本指南为618大促期间直播话术提供标准化模板，涵盖开场引流、产品介绍、互动促单、收尾等全流程话术，帮助主播快速掌握大促直播节奏。',
    sections: [
      {
        heading: '一、开场引流话术',
        paragraphs: [
          '直播开场前3分钟是留住观众的关键时段，需要迅速建立信任感和紧迫感。以下为推荐的开场话术模板：'
        ],
        listItems: [
          '欢迎新进直播间的宝宝们！今天是618超级大促专场，全场满300减50，还有神秘大礼等着你们！',
          '先点关注不迷路，右上角点个关注，优惠信息第一时间收到！',
          '今天直播间准备了200份秒杀福利，只有关注了的宝宝才能参加哦！',
          '倒计时3分钟，我们的第一个爆款即将开秒！准备好你们的小手！'
        ]
      },
      {
        heading: '二、产品介绍话术',
        paragraphs: [
          '产品介绍遵循"痛点-方案-效果-价格"四步法，让观众感受到产品的必要性和性价比。'
        ],
        listItems: [
          '先说痛点：「姐妹们，你们是不是经常熬夜导致皮肤暗沉？特别是眼下细纹越来越多？」',
          '再说方案：「这款玻尿酸精华液，专补水不黏腻，30ml小分子深层渗透，用完第二天皮肤就像喝饱了水」',
          '展示效果：「大家看我的手背对比，左边是没涂的，右边涂了一分钟，是不是明显亮了一个色号？」',
          '公布价格：「专柜价399，今天618直播间只要299，还送同款旅行装10ml！」'
        ]
      },
      {
        heading: '三、互动促单话术',
        paragraphs: [
          '在直播中段需要持续调动观众积极性，通过互动制造购买氛围。'
        ],
        listItems: [
          '想要的宝宝扣1，满100人我再降20块！',
          '后台告诉我已经有多少人加购了，哇，300多个宝宝都在抢！',
          '最后50单！拍完不补货了，厂家就给了这么多库存！',
          '5、4、3、2、1，上车！'
        ]
      },
      {
        heading: '四、收尾话术',
        paragraphs: [
          '直播结束前需要做好收尾和预告，为下一场直播蓄水。'
        ],
        listItems: [
          '今天辛苦各位宝宝陪伴，我们的下一场直播在明天晚上8点，记得关注不迷路！',
          '还没下单的宝宝抓紧最后10分钟，过了12点所有优惠全部恢复原价！',
          '感谢每一位支持的宝宝，你们的支持是我们最大的动力，明天见！'
        ]
      }
    ]
  },
  '2': {
    title: '护肤品类专业话术手册',
    author: '赵丽丽',
    updatedAt: '2026-06-03',
    category: '直播话术',
    summary: '本手册整理了护肤品类产品的专业话术，包括成分讲解、功效说明、使用方法等，帮助主播更专业地向观众介绍护肤产品。',
    sections: [
      {
        heading: '一、清洁类产品话术',
        paragraphs: [
          '清洁是护肤的第一步，好的清洁产品能为后续护肤打下良好基础。'
        ],
        listItems: [
          '氨基酸洁面乳：温和不紧绷，适合所有肤质，尤其是敏感肌',
          '卸妆油：以油溶油原理，彻底卸除彩妆残留',
          '清洁面膜：深层清洁毛孔，控油抑痘'
        ]
      },
      {
        heading: '二、保湿类产品话术',
        paragraphs: [
          '保湿是护肤的核心步骤，缺水会导致各种肌肤问题。'
        ],
        listItems: [
          '玻尿酸精华液：小分子玻尿酸深层补水，大分子表面锁水',
          '保湿面霜：神经酰胺修护屏障，质地清爽不油腻',
          '睡眠面膜：夜间集中修护，第二天醒来水润饱满'
        ]
      }
    ]
  }
}

// Default fallback for any ID
const defaultDoc = mockDocs['1']

async function loadDetail(id) {
  try {
    const res = await KnowledgeAPI.detail(id)
    document.value = res.data || mockDocs[id] || defaultDoc
  } catch {
    document.value = mockDocs[id] || defaultDoc
  }
}

onLoad((query) => {
  docId.value = query.id || '1'
  loadDetail(docId.value)
})
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
  padding: 28rpx;
  margin-bottom: 24rpx;
}

.header-card {
  margin: 24rpx 32rpx 0;
}

.doc-title {
  font-size: 36rpx;
  font-weight: 700;
  color: $text-primary;
  line-height: 1.4;
  margin-bottom: 16rpx;
  display: block;
}

.meta-row {
  display: flex;
  gap: 24rpx;
  margin-bottom: 12rpx;
}

.meta-item {
  font-size: 24rpx;
  color: $text-muted;
}

.doc-tag {
  font-size: 22rpx;
  padding: 4rpx 14rpx;
  border-radius: 8rpx;
  display: inline-block;

  &.tag-直播话术 { background: rgba($neon-purple, 0.15); color: $neon-purple; }
  &.tag-运营规范 { background: rgba($neon-cyan, 0.15); color: $neon-cyan; }
  &.tag-产品知识 { background: rgba($neon-green, 0.15); color: $neon-green; }
  &.tag-培训资料 { background: rgba($neon-yellow, 0.15); color: $neon-yellow; }
  &.tag-公司制度 { background: rgba($neon-pink, 0.15); color: $neon-pink; }
}

.content-scroll {
  flex: 1;
  padding: 0 32rpx;
}

.content-card {
  margin-bottom: 0;
}

.content-block {
  margin-bottom: 32rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.block-title {
  font-size: 30rpx;
  font-weight: 600;
  color: $neon-cyan;
  margin-bottom: 16rpx;
  display: block;
}

.block-text {
  font-size: 28rpx;
  color: $text-secondary;
  line-height: 1.7;
  margin-bottom: 12rpx;
  display: block;
}

.block-list {
  margin-top: 12rpx;
  padding: 16rpx;
  background: rgba($neon-purple, 0.06);
  border-radius: $radius-sm;
  border-left: 4rpx solid $neon-purple;
}

.list-item {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
  margin-bottom: 12rpx;

  &:last-child {
    margin-bottom: 0;
  }
}

.list-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: $neon-purple;
  margin-top: 14rpx;
  flex-shrink: 0;
  box-shadow: 0 0 8rpx rgba($neon-purple, 0.5);
}

.list-text {
  font-size: 26rpx;
  color: $text-secondary;
  line-height: 1.6;
  flex: 1;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
