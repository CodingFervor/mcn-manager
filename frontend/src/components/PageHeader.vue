<script setup>
defineProps({
  title: String,
  subtitle: String,
})
</script>

<template>
  <div style="margin-bottom: 20px">
    <h2 class="page-title">{{ title }}</h2>
    <p class="page-subtitle" v-if="subtitle">{{ subtitle }}</p>
  </div>
</template>
