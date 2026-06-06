<template>
  <view class="page">
    <!-- Search Bar -->
    <view class="search-bar">
      <view class="search-input-wrap">
        <text class="search-icon">&#128269;</text>
        <input
          class="search-input"
          v-model="keyword"
          placeholder="搜索商品名称"
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

    <!-- Product Grid -->
    <scroll-view scroll-y class="product-grid" @scrolltolower="onReachBottom">
      <view class="grid-row">
        <view
          v-for="product in filteredProducts"
          :key="product.id"
          class="glass-card product-card"
        >
          <view :class="['product-img', `img-${product.category}`]">
            <text class="img-text">{{ product.name.substring(0, 2) }}</text>
          </view>
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <view class="price-row">
              <text class="product-price">{{ formatMoney(product.price) }}</text>
              <text class="product-stock">库存: {{ product.stock }}</text>
            </view>
          </view>
        </view>
      </view>

      <view v-if="filteredProducts.length === 0" class="empty-tip">
        <text class="tip-text">暂无商品</text>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onPullDownRefresh, onReachBottom } from '@dcloudio/uni-app'
import { ProductAPI } from '@/api'
import { formatMoney } from '@/utils/format'

const keyword = ref('')
const activeCategory = ref('全部')
const products = ref([])

const categories = ['全部', '护肤', '彩妆', '个护', '工具', '套装']

const mockProducts = [
  { id: 1, name: '玻尿酸精华液30ml', price: 299, stock: 580, category: '护肤' },
  { id: 2, name: '烟酰胺美白面霜50g', price: 300, stock: 420, category: '护肤' },
  { id: 3, name: '氨基酸洁面乳120ml', price: 100, stock: 860, category: '护肤' },
  { id: 4, name: '防晒喷雾SPF50+', price: 245, stock: 320, category: '护肤' },
  { id: 5, name: '丝绒雾面唇釉', price: 128, stock: 750, category: '彩妆' },
  { id: 6, name: '12色眼影盘大地色', price: 198, stock: 290, category: '彩妆' },
  { id: 7, name: '持久定妆粉饼', price: 158, stock: 410, category: '彩妆' },
  { id: 8, name: '防水眼线笔', price: 68, stock: 920, category: '彩妆' },
  { id: 9, name: '电动洁面仪', price: 399, stock: 150, category: '工具' },
  { id: 10, name: '化妆刷套装12支', price: 168, stock: 380, category: '工具' },
  { id: 11, name: '美妆蛋3枚装', price: 39, stock: 1200, category: '工具' },
  { id: 12, name: '滋养身体乳300ml', price: 89, stock: 640, category: '个护' },
  { id: 13, name: '氨基酸洗发水500ml', price: 79, stock: 520, category: '个护' },
  { id: 14, name: '护手霜礼盒5支', price: 128, stock: 300, category: '个护' },
  { id: 15, name: '护肤四件套礼盒', price: 699, stock: 180, category: '套装' },
  { id: 16, name: '焕彩美妆礼盒', price: 499, stock: 120, category: '套装' }
]

const filteredProducts = computed(() => {
  let list = products.value
  if (activeCategory.value !== '全部') {
    list = list.filter(p => p.category === activeCategory.value)
  }
  if (keyword.value.trim()) {
    const kw = keyword.value.trim().toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(kw))
  }
  return list
})

function onSearch() {
  // keyword is reactive, filteredProducts auto updates
}

async function loadData() {
  try {
    const res = await ProductAPI.list()
    products.value = res.data?.results || res.data || mockProducts
  } catch {
    products.value = mockProducts
  }
}

onShow(() => {
  loadData()
})

onPullDownRefresh(async () => {
  await loadData()
  uni.stopPullDownRefresh()
})

onReachBottom(() => {
  // pagination could be added here
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

.product-grid {
  padding: 0 32rpx;
  height: calc(100vh - 260rpx);
}

.grid-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.glass-card {
  background: $bg-card;
  border: 2rpx solid $border-glow;
  border-radius: $radius-md;
  backdrop-filter: blur(20rpx);
}

.product-card {
  width: calc(50% - 8rpx);
  overflow: hidden;
  margin-bottom: 0;
}

.product-img {
  width: 100%;
  height: 260rpx;
  display: flex;
  align-items: center;
  justify-content: center;

  &.img-护肤 { background: linear-gradient(135deg, rgba($neon-purple, 0.3), rgba($neon-pink, 0.2)); }
  &.img-彩妆 { background: linear-gradient(135deg, rgba($neon-pink, 0.3), rgba($neon-yellow, 0.2)); }
  &.img-工具 { background: linear-gradient(135deg, rgba($neon-cyan, 0.3), rgba($neon-green, 0.2)); }
  &.img-个护 { background: linear-gradient(135deg, rgba($neon-green, 0.3), rgba($neon-cyan, 0.2)); }
  &.img-套装 { background: linear-gradient(135deg, rgba($neon-yellow, 0.3), rgba($neon-purple, 0.2)); }
}

.img-text {
  font-size: 48rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
}

.product-info {
  padding: 16rpx 20rpx 20rpx;
}

.product-name {
  font-size: 26rpx;
  color: $text-primary;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12rpx;
  line-height: 1.4;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.product-price {
  font-size: 30rpx;
  font-weight: 700;
  color: $neon-pink;
}

.product-stock {
  font-size: 22rpx;
  color: $text-muted;
}

.empty-tip {
  width: 100%;
  padding: 80rpx 0;
  text-align: center;
}

.tip-text {
  font-size: 28rpx;
  color: $text-muted;
}
</style>
