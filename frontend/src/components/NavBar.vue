<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'

const router = useRouter()
const route = useRoute()
const { t, locale, setLocale } = useI18n()
const { isDark, toggleTheme } = useTheme()

const isAdmin = localStorage.getItem('isAdmin') === 'true'
const username = localStorage.getItem('username')

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('isAdmin')
  router.push('/login')
}
</script>

<template>
  <nav class="navbar">
    <div class="nav-left">
      <div class="logo-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
      </div>
      <span class="app-title">{{ t('appTitle') }}</span>
      
      <div class="nav-menu">
        <router-link 
          to="/query" 
          class="nav-link"
          :class="{ active: route.path === '/query' }"
        >
          {{ t('queryRecordings') }}
        </router-link>
        <router-link 
          to="/import" 
          class="nav-link"
          :class="{ active: route.path === '/import' }"
        >
          {{ t('importRecordings') }}
        </router-link>
        <router-link 
          v-if="isAdmin"
          to="/users" 
          class="nav-link"
          :class="{ active: route.path === '/users' }"
        >
          {{ t('userManagement') }}
        </router-link>
      </div>
    </div>
    
    <div class="nav-right">
      <span class="user-info">
        <span class="user-name">{{ username }}</span>
        <span v-if="isAdmin" class="admin-badge">{{ t('admin') }}</span>
      </span>
      <button @click="logout" class="btn-logout">{{ t('logout') }}</button>
      
      <div class="language-dropdown">
        <select :value="locale" @change="setLocale($event.target.value)">
          <option value="en">English</option>
          <option value="zh">中文</option>
        </select>
      </div>
      
      <button class="icon-btn" @click="toggleTheme" :title="isDark ? t('theme.light') : t('theme.dark')">
        <svg v-if="isDark" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  margin-bottom: 24px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  gap: 4px;
  margin-left: 24px;
}

.nav-link {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  min-width: 80px;
  text-align: center;
}

.nav-link:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.nav-link.active {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn svg {
  width: 18px;
  height: 18px;
}

.icon-btn:hover {
  background: var(--bg-tertiary);
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-name {
  color: var(--text-secondary);
  font-size: 14px;
}

.admin-badge {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.btn-logout {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-logout:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.language-dropdown {
}

.language-dropdown select {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-display);
  cursor: pointer;
  outline: none;
}

.language-dropdown select:hover {
  border-color: var(--accent-primary);
}
</style>
