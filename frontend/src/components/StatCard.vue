<script setup>
defineProps({
  label: String,
  value: [String, Number],
  sub: String,
  icon: String,
  gradient: { type: String, default: 'g1' },
  trend: String,
})
</script>

<template>
  <div :class="['stat-card', gradient]">
    <span class="stat-icon">{{ icon }}</span>
    <div class="stat-label">{{ label }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-sub" v-if="sub">{{ sub }}</div>
    <div class="stat-trend" v-if="trend">{{ trend }}</div>
  </div>
</template>
