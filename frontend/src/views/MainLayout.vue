<script setup>
import NavBar from '../components/NavBar.vue'
</script>

<template>
  <div class="layout">
    <NavBar />
    <router-view />
  </div>
</template>

<style scoped>
.layout {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
