<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import appConfig from '../config.js'

const router = useRouter()
const API_URL = appConfig.apiUrl
const { t } = useI18n()
useTheme()

const token = ref(localStorage.getItem('token'))
const currentUserId = ref(parseInt(localStorage.getItem('userId') || '0'))
const users = ref([])
const newUserForm = ref({ username: '', password: '' })
const loading = ref(true)

onMounted(async () => {
  if (!localStorage.getItem('isAdmin')) {
    router.push('/query')
    return
  }
  await fetchUsers()
})

async function fetchUsers() {
  loading.value = true
  try {
    const res = await axios.get(`${API_URL}/users`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    users.value = res.data
  } catch (e) {
    console.error('Error fetching users:', e)
  } finally {
    loading.value = false
  }
}

async function createUser() {
  if (!newUserForm.value.username || !newUserForm.value.password) {
    await window.$modal.alert('Please enter username and password')
    return
  }
  try {
    await axios.post(`${API_URL}/users`, newUserForm.value, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    newUserForm.value = { username: '', password: '' }
    await fetchUsers()
  } catch (e) {
    await window.$modal.alert(e.response?.data?.detail || 'Failed to create user', 'Error')
  }
}

async function deleteUser(userId) {
  try {
    await window.$modal.confirm('Are you sure you want to delete this user?', 'Delete User')
    try {
      await axios.delete(`${API_URL}/users/${userId}`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      await fetchUsers()
    } catch (e) {
      await window.$modal.alert(e.response?.data?.detail || 'Failed to delete user', 'Error')
    }
  } catch {}
}

const userCount = computed(() => users.value.length)
</script>

<template>
  <div class="users-page">
    <div class="panel-header">
      <h2>{{ t('users.title') }}</h2>
      <span class="user-count">{{ userCount }} users</span>
    </div>
    
    <div class="create-user-form">
      <input v-model="newUserForm.username" :placeholder="t('users.username')" />
      <input v-model="newUserForm.password" type="password" :placeholder="t('users.password')" />
      <button @click="createUser" class="btn-primary">{{ t('users.createUser') }}</button>
    </div>
    
    <div class="users-list" v-if="!loading">
      <div v-if="users.length === 0" class="empty-state">
        No users found
      </div>
      <div 
        v-for="u in users" 
        :key="u.id" 
        class="user-item"
        :data-id="u.id"
        :data-username="u.username"
        :data-is-admin="u.is_admin"
      >
        <span class="user-name">[{{ u.id }}] {{ u.username }}</span>
        <span v-if="u.is_admin === true || u.is_admin === 1" class="admin-badge">{{ t('users.admin') }}</span>
        <button 
          v-if="(u.is_admin === 0 || u.is_admin === false) && u.id !== currentUserId" 
          @click="deleteUser(u.id)" 
          class="btn-danger"
        >
          {{ t('users.delete') }}
        </button>
      </div>
    </div>
    
    <div v-else class="loading-state">
      Loading...
    </div>
  </div>
</template>

<style scoped>
.users-page {
  max-width: 1400px;
  margin: 0 auto;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px 12px 0 0;
}

.panel-header h2 {
  font-size: 16px;
  font-weight: 600;
}

.user-count {
  font-size: 13px;
  color: var(--text-secondary);
}

.create-user-form {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-top: none;
}

.create-user-form input {
  flex: 1;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-display);
}

.create-user-form input:focus {
  outline: none;
  border-color: var(--accent-primary);
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--accent-glow);
}

.users-list {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-top: none;
  border-radius: 0 0 12px 12px;
  padding: 0 24px;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.user-item:last-child {
  border-bottom: none;
}

.user-name {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

.admin-badge {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.btn-danger {
  padding: 8px 16px;
  background: var(--danger);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background: var(--danger-hover);
}

.empty-state, .loading-state {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}
</style>
