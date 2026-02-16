<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'

const API_URL = '/api'
const { t } = useI18n()
useTheme()

const token = localStorage.getItem('token')

const queryForm = ref({
  start_time: '',
  end_time: '',
  participant_name: ''
})
const recordings = ref([])
const isQuerying = ref(false)
const isImporting = ref(false)
const queryError = ref('')
const importProgress = ref('')

const selectedIds = ref(new Set())
const isSelectAll = ref(false)

const HISTORY_KEY = 'importSearchHistory'
const MAX_HISTORY = 3
const searchHistory = ref([])

function loadHistory() {
  const saved = localStorage.getItem(HISTORY_KEY)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      searchHistory.value = parsed.filter(h => h.label)
    } catch {
      searchHistory.value = []
    }
  }
}

function saveToHistory() {
  if (!queryForm.value.start_time && !queryForm.value.end_time) return
  
  const label = queryForm.value.participant_name 
    ? `${queryForm.value.participant_name} (${queryForm.value.start_time?.slice(0, 16)} - ${queryForm.value.end_time?.slice(0, 16)})`
    : `${queryForm.value.start_time?.slice(0, 16)} - ${queryForm.value.end_time?.slice(0, 16)}`
  
  const historyItem = {
    label,
    start_time: queryForm.value.start_time,
    end_time: queryForm.value.end_time,
    participant_name: queryForm.value.participant_name
  }
  
  searchHistory.value = [historyItem, ...searchHistory.value.filter(h => h.label !== label)].slice(0, MAX_HISTORY)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

function applyHistoryItem(item) {
  queryForm.value.start_time = item.start_time
  queryForm.value.end_time = item.end_time
  queryForm.value.participant_name = item.participant_name
}

function clearHistory() {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
}

loadHistory()

async function queryRecordings() {
  queryError.value = ''
  isQuerying.value = true
  recordings.value = []
  selectedIds.value.clear()
  isSelectAll.value = false
  try {
    const response = await axios.post(`${API_URL}/query/vfc`, queryForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    recordings.value = response.data
    if (response.data.length === 0) {
      queryError.value = t('query.noRecordings')
    }
    saveToHistory()
  } catch (e) {
    queryError.value = e.response?.data?.detail || 'Query failed'
  } finally {
    isQuerying.value = false
  }
}

function toggleSelect(ccrdId) {
  if (selectedIds.value.has(ccrdId)) {
    selectedIds.value.delete(ccrdId)
  } else {
    selectedIds.value.add(ccrdId)
  }
  selectedIds.value = new Set(selectedIds.value)
}

function toggleSelectAll() {
  if (isSelectAll.value) {
    selectedIds.value.clear()
  } else {
    recordings.value.forEach(r => selectedIds.value.add(r.ccrd_id))
  }
  selectedIds.value = new Set(selectedIds.value)
  isSelectAll.value = !isSelectAll.value
}

function isSelected(ccrdId) {
  return selectedIds.value.has(ccrdId)
}

async function importSelected() {
  if (selectedIds.value.size === 0) {
    await window.$modal.alert('Please select at least one recording to import')
    return
  }
  
  isImporting.value = true
  importProgress.value = ''
  
  const selectedRecordings = recordings.value.filter(r => selectedIds.value.has(r.ccrd_id))
  
  try {
    const response = await axios.post(`${API_URL}/import`, {
      recordings: selectedRecordings
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const imported = response.data.imported?.length || 0
    const failed = response.data.failed?.length || 0
    
    await window.$modal.alert(`Import completed: ${imported} succeeded, ${failed} failed`)
    
    selectedIds.value.clear()
    isSelectAll.value = false
    
  } catch (e) {
    await window.$modal.alert(e.response?.data?.detail || 'Import failed', 'Error')
  } finally {
    isImporting.value = false
    importProgress.value = ''
  }
}

function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatDateTime(dateStr) {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString()
  } catch {
    return dateStr
  }
}
</script>

<template>
  <div class="import-page">
    <div class="panel-header">
      <h2>{{ t('import.title') }}</h2>
    </div>
    
    <form @submit.prevent="queryRecordings" class="query-form">
      <div class="form-row">
        <div class="form-group">
          <label>{{ t('query.startTime') }}</label>
          <input 
            type="datetime-local" 
            v-model="queryForm.start_time" 
            required
          />
        </div>
        <div class="form-group">
          <label>{{ t('query.endTime') }}</label>
          <input 
            type="datetime-local" 
            v-model="queryForm.end_time" 
            required
          />
        </div>
        <div class="form-group">
          <label>{{ t('query.participantName') }}</label>
          <input 
            type="text" 
            v-model="queryForm.participant_name" 
            :placeholder="t('query.searchByParticipant')"
          />
        </div>
      </div>
      
      <div class="form-actions-row">
        <button type="submit" class="btn-primary" :disabled="isQuerying">
          <span v-if="isQuerying" class="spinner"></span>
          {{ isQuerying ? t('query.searching') : t('query.search') }}
        </button>
        
        <div v-if="searchHistory.length > 0" class="search-history">
          <span class="history-label">{{ t('query.recentSearches') }}:</span>
          <button 
            v-for="(item, index) in searchHistory" 
            :key="index"
            type="button"
            @click="applyHistoryItem(item)"
            class="history-item"
          >
            {{ item.label }}
          </button>
          <button type="button" class="history-clear" @click="clearHistory">
            {{ t('query.clearHistory') }}
          </button>
        </div>
      </div>
    </form>
    
    <div class="results-section">
      <div class="panel-header">
        <h2>{{ t('query.results') }}</h2>
        <div class="header-actions">
          <span class="result-count" v-if="recordings.length">
            {{ selectedIds.size }} / {{ recordings.length }} {{ t('import.selected') }}
          </span>
        </div>
      </div>
      
      <div v-if="queryError" class="info-message">{{ queryError }}</div>
      
      <div v-if="recordings.length > 0" class="table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th class="col-checkbox">
                <input 
                  type="checkbox" 
                  :checked="isSelectAll"
                  @click="toggleSelectAll"
                />
              </th>
              <th>ID</th>
              <th>{{ t('player.userName') }}</th>
              <th>{{ t('player.startTime') }}</th>
              <th>{{ t('query.endTime') }}</th>
              <th>{{ t('player.duration') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in recordings" :key="rec.ccrd_id" @click="toggleSelect(rec.ccrd_id)" :class="{ selected: isSelected(rec.ccrd_id) }">
              <td class="col-checkbox">
                <input 
                  type="checkbox" 
                  :checked="isSelected(rec.ccrd_id)"
                  @click.stop="toggleSelect(rec.ccrd_id)"
                />
              </td>
              <td class="mono">{{ rec.ccrd_id }}</td>
              <td>{{ rec.verba_user_name }}</td>
              <td>{{ formatDateTime(rec.start_time) }}</td>
              <td>{{ formatDateTime(rec.end_time) }}</td>
              <td class="mono">{{ formatDuration(rec.duration) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-else-if="!queryError" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <p>{{ t('query.emptyState') }}</p>
      </div>
      
      <div class="import-actions" v-if="recordings.length > 0">
        <span class="import-count">{{ selectedIds.size }} {{ t('import.selected') }}</span>
        <button 
          @click="importSelected" 
          class="btn-import" 
          :disabled="selectedIds.size === 0 || isImporting"
        >
          <span v-if="isImporting" class="spinner"></span>
          {{ isImporting ? t('import.importing') : t('import.import') }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.import-page {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-count {
  color: var(--text-secondary);
  font-size: 13px;
}

.query-form {
  padding: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-top: none;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.form-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.form-actions-row .btn-primary {
  flex-shrink: 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input {
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-display);
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.btn-primary {
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 8px 16px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 13px;
  cursor: pointer;
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
}

.results-section {
  margin-top: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.info-message {
  margin: 16px 24px;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
}

.table-container {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th,
.results-table td {
  padding: 14px 20px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.results-table th {
  background: var(--bg-tertiary);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.results-table tr {
  cursor: pointer;
}

.results-table tr:hover td {
  background: var(--bg-tertiary);
}

.results-table tr.selected td {
  background: rgba(16, 185, 129, 0.1);
}

.col-checkbox {
  width: 40px;
}

.col-checkbox input {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.mono {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
}

.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: var(--text-muted);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 14px;
}

.import-actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
}

.import-count {
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-import {
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-import:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.search-history {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.history-label {
  font-size: 13px;
  color: var(--text-muted);
}

.history-item {
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.history-clear {
  padding: 6px 12px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-clear:hover {
  color: var(--danger);
}
</style>
