<script setup>
import { onMounted, ref } from 'vue'
import { useTheme } from './composables/useTheme'
import Modal from './components/Modal.vue'

const modalRef = ref(null)

onMounted(() => {
  useTheme()
})

window.$modal = {
  alert: (msg, title) => modalRef.value?.alert(msg, title),
  confirm: (msg, title) => modalRef.value?.confirmDialog(msg, title)
}
</script>

<template>
  <div class="app">
    <div class="bg-pattern"></div>
    <router-view />
    <Modal ref="modalRef" />
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-primary: #0a0f14;
  --bg-secondary: #111920;
  --bg-tertiary: #1a232d;
  --bg-elevated: #222d3a;
  --accent-primary: #10b981;
  --accent-secondary: #059669;
  --accent-glow: rgba(16, 185, 129, 0.2);
  --text-primary: #f0f4f8;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --border-color: #2d3f52;
  --danger: #ef4444;
  --danger-hover: #dc2626;
  --font-display: 'Outfit', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

body {
  font-family: var(--font-display);
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
  overflow-y: scroll;
}

.app {
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  padding: 24px;
}

.bg-pattern {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(ellipse at 20% 20%, rgba(16, 185, 129, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
    linear-gradient(180deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  pointer-events: none;
  z-index: 0;
}

.app > *:not(.bg-pattern) {
  position: relative;
  z-index: 1;
}
</style>
