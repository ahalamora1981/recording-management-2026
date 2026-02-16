import { ref, computed, watch } from 'vue'

const currentTheme = ref(localStorage.getItem('theme') || 'dark')

export function useTheme() {
  const isDark = computed(() => currentTheme.value === 'dark')
  
  function toggleTheme() {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', currentTheme.value)
    applyTheme()
  }
  
  function applyTheme() {
    const root = document.documentElement
    if (currentTheme.value === 'dark') {
      root.style.setProperty('--bg-primary', '#0a0f14')
      root.style.setProperty('--bg-secondary', '#111920')
      root.style.setProperty('--bg-tertiary', '#1a232d')
      root.style.setProperty('--bg-elevated', '#222d3a')
      root.style.setProperty('--text-primary', '#f0f4f8')
      root.style.setProperty('--text-secondary', '#94a3b8')
      root.style.setProperty('--text-muted', '#64748b')
      root.style.setProperty('--border-color', '#2d3f52')
    } else {
      root.style.setProperty('--bg-primary', '#f8fafc')
      root.style.setProperty('--bg-secondary', '#ffffff')
      root.style.setProperty('--bg-tertiary', '#f1f5f9')
      root.style.setProperty('--bg-elevated', '#e2e8f0')
      root.style.setProperty('--text-primary', '#1e293b')
      root.style.setProperty('--text-secondary', '#64748b')
      root.style.setProperty('--text-muted', '#94a3b8')
      root.style.setProperty('--border-color', '#e2e8f0')
    }
  }
  
  watch(currentTheme, applyTheme, { immediate: true })
  
  return { isDark, toggleTheme, applyTheme }
}
