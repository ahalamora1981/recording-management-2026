<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import AudioPlayer from '../components/AudioPlayer.vue'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import appConfig from '../config.js'

const API_URL = appConfig.apiUrl
const { t } = useI18n()
useTheme()

const token = ref(localStorage.getItem('token'))

const queryForm = ref({
  start_time: '',
  end_time: '',
  participant_name: ''
})
const recordings = ref([])
const isQuerying = ref(false)
const queryError = ref('')
const searchHistory = ref([])

const downloadedFiles = ref({})
const downloadingIds = ref(new Set())
const showPlayer = ref(false)
const currentRecording = ref(null)
const selectedIds = ref(new Set())

const isSelectAll = ref(false)
const currentPage = ref(1)
const itemsPerPage = appConfig.itemsPerPage

const paginatedRecords = ref([])

const totalPages = computed(() => Math.ceil(recordings.value.length / itemsPerPage))

function updatePaginatedRecords() {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  paginatedRecords.value = recordings.value.slice(start, end)
}

const visiblePages = computed(() => {
  const pages = []
  const current = currentPage.value
  const total = totalPages.value
  const delta = 5
  
  let start = Math.max(1, current - delta)
  let end = Math.min(total, current + delta)
  
  if (current - delta < 1) {
    end = Math.min(total, end + (delta - current + 1))
  }
  if (current + delta > total) {
    start = Math.max(1, start - (current + delta - total))
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    updatePaginatedRecords()
    updateSelectAll()
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    updatePaginatedRecords()
    updateSelectAll()
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    updatePaginatedRecords()
    updateSelectAll()
  }
}

function isSelected(ccrdId) {
  return selectedIds.value.has(ccrdId)
}

function toggleSelect(ccrdId) {
  if (selectedIds.value.has(ccrdId)) {
    selectedIds.value.delete(ccrdId)
  } else {
    selectedIds.value.add(ccrdId)
  }
  selectedIds.value = new Set(selectedIds.value)
  updateSelectAll()
}

function toggleSelectAll() {
  const currentPageIds = paginatedRecords.value.map(r => r.ccrd_id)
  const allCurrentPageSelected = currentPageIds.every(id => selectedIds.value.has(id))
  
  if (allCurrentPageSelected) {
    currentPageIds.forEach(id => selectedIds.value.delete(id))
  } else {
    currentPageIds.forEach(id => selectedIds.value.add(id))
  }
  selectedIds.value = new Set(selectedIds.value)
  updateSelectAll()
}

function updateSelectAll() {
  const currentPageIds = paginatedRecords.value.map(r => r.ccrd_id)
  const allCurrentPageSelected = currentPageIds.length > 0 && currentPageIds.every(id => selectedIds.value.has(id))
  isSelectAll.value = allCurrentPageSelected
}

async function confirmDeleteAll() {
  try {
    await window.$modal.confirm(
      `Are you sure you want to delete ${selectedIds.value.size} recording(s)?`, 
      t('query.delete')
    )
    await deleteSelected()
  } catch {}
}

async function deleteSelected() {
  const idsToDelete = Array.from(selectedIds.value)
  
  for (const ccrdId of idsToDelete) {
    try {
      await axios.delete(`${API_URL}/recordings/${ccrdId}`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      recordings.value = recordings.value.filter(r => r.ccrd_id !== ccrdId)
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }
  
  if (currentPage.value > totalPages.value) {
    currentPage.value = Math.max(1, totalPages.value)
  }
  updatePaginatedRecords()
  selectedIds.value.clear()
  selectedIds.value = new Set(selectedIds.value)
  updateSelectAll()
}

const HISTORY_KEY = 'searchHistory'
const MAX_HISTORY = 3

onMounted(() => {
  const saved = localStorage.getItem(HISTORY_KEY)
  if (saved) {
    try {
      const parsed = JSON.parse(saved)
      searchHistory.value = parsed.filter(h => h.label)
    } catch {
      searchHistory.value = []
    }
  }
})

function saveToHistory() {
  const label = formatHistoryLabel(queryForm.value.start_time, queryForm.value.end_time)
  if (!label) return
  
  const historyItem = {
    start_time: queryForm.value.start_time,
    end_time: queryForm.value.end_time,
    participant_name: queryForm.value.participant_name,
    label: label
  }
  
  searchHistory.value = [historyItem, ...searchHistory.value.filter(h => h.label !== historyItem.label)].slice(0, MAX_HISTORY)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

function formatHistoryLabel(start, end) {
  if (!start || !end) return ''
  try {
    const s = new Date(start)
    const e = new Date(end)
    return `${s.toLocaleDateString()} ${s.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - ${e.toLocaleDateString()} ${e.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`
  } catch {
    return ''
  }
}

function loadFromHistory(item) {
  queryForm.value.start_time = item.start_time
  queryForm.value.end_time = item.end_time
  queryForm.value.participant_name = item.participant_name || ''
}

function clearHistory() {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
}

async function queryRecordings() {
  if (!token.value) {
    queryError.value = 'Not logged in'
    return
  }
  
  queryError.value = ''
  isQuerying.value = true
  recordings.value = []
  selectedIds.value.clear()
  currentPage.value = 1
  
  try {
    const response = await axios.post(`${API_URL}/query`, queryForm.value, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    
    if (!response.data || response.data.length === 0) {
      queryError.value = t('query.noRecordings')
      return
    }
    
    recordings.value = response.data
    saveToHistory()
    updatePaginatedRecords()
    updateSelectAll()
  } catch (e) {
    queryError.value = e.response?.data?.detail || 'Query failed'
  } finally {
    isQuerying.value = false
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

async function downloadRecording(ccrdId) {
  downloadingIds.value.add(ccrdId)
  try {
    const response = await axios.get(`${API_URL}/download/${ccrdId}`, {
      headers: { Authorization: `Bearer ${token.value}` },
      responseType: 'blob'
    })
    const blob = new Blob([response.data], { type: 'audio/mpeg' })
    const url = URL.createObjectURL(blob)
    downloadedFiles.value[ccrdId] = url
  } catch (e) {
    await window.$modal.alert('Failed to download recording', 'Error')
  } finally {
    downloadingIds.value.delete(ccrdId)
  }
}

function playRecording(ccrdId) {
  const recording = recordings.value.find(r => r.ccrd_id === ccrdId)
  if (!recording) return
  
  currentRecording.value = { ...recording }
  showPlayer.value = true
}

async function deleteRecording(ccrdId) {
  try {
    await window.$modal.confirm(t('query.confirmDelete'), t('query.delete'))
    try {
      await axios.delete(`${API_URL}/recordings/${ccrdId}`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      await queryRecordings()
    } catch (e) {
      await window.$modal.alert(e.response?.data?.detail || 'Failed to delete recording', 'Error')
    }
  } catch {}
}

function closePlayer() {
  showPlayer.value = false
  currentRecording.value = null
}

function onTranscribed({ ccrdId, transcription }) {
  const rec = recordings.value.find(r => r.ccrd_id === ccrdId)
  if (rec) {
    rec.transcribed = transcription && transcription.trim() ? 'Yes' : 'No'
  }
  const paginated = paginatedRecords.value.find(r => r.ccrd_id === ccrdId)
  if (paginated) {
    paginated.transcribed = transcription && transcription.trim() ? 'Yes' : 'No'
  }
}

function stopPlayback() {
  downloadedFiles.value = {}
}

function isDownloaded(ccrdId) {
  return !!downloadedFiles.value[ccrdId]
}
</script>

<template>
  <div class="query-page">
    <div class="panel-header">
      <h2>{{ t('query.title') }}</h2>
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
            class="history-item"
            @click="loadFromHistory(item)"
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
        <span class="result-count" v-if="recordings.length">{{ recordings.length }} {{ t('query.recordingsFound') }}</span>
      </div>
      
      <div v-if="queryError" class="info-message">{{ t('query.noRecordings') }}</div>
      
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
              <th>{{ t('player.startTime') }}</th>
              <th>{{ t('player.duration') }}</th>
              <th>{{ t('query.channel') }}</th>
              <th>{{ t('player.userName') }}</th>
              <th>{{ t('query.transcribed') }}</th>
              <th>{{ t('query.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rec in paginatedRecords" :key="rec.ccrd_id">
              <td class="col-checkbox">
                <input 
                  type="checkbox" 
                  :checked="isSelected(rec.ccrd_id)"
                  @click="toggleSelect(rec.ccrd_id)"
                />
              </td>
              <td>{{ formatDateTime(rec.start_time) }}</td>
              <td class="mono">{{ formatDuration(rec.duration) }}</td>
              <td>{{ rec.channel || 'call' }}</td>
              <td>{{ rec.verba_user_name }}</td>
              <td>
                <span :class="rec.transcribed === 'Yes' ? 'transcribed-yes' : 'transcribed-no'">
                  {{ rec.transcribed }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button 
                    @click="playRecording(rec.ccrd_id)" 
                    class="btn-play"
                  >
                    {{ t('query.details') }}
                  </button>
                  <button 
                    @click="deleteRecording(rec.ccrd_id)" 
                    class="btn-delete"
                  >
                    {{ t('query.delete') }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div class="bulk-actions" v-if="selectedIds.size > 0">
          <button @click="confirmDeleteAll" class="btn-delete-all">
            {{ t('query.deleteSelected') }} ({{ selectedIds.size }})
          </button>
        </div>
        
        <div class="pagination" v-if="totalPages > 1">
          <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">
            &lt;
          </button>
          <template v-for="page in visiblePages" :key="page">
            <button 
              @click="goToPage(page)" 
              class="page-btn"
              :class="{ active: page === currentPage }"
            >
              {{ page }}
            </button>
          </template>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">
            &gt;
          </button>
        </div>
      </div>
      
      <div v-else-if="!queryError" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <p>{{ t('query.emptyState') }}</p>
      </div>
      </div>
    
    <AudioPlayer 
      :show="showPlayer" 
      :recording="currentRecording" 
      :ccrd-id="currentRecording?.ccrd_id"
      :auto-transcribe="appConfig.autoTranscribe"
      @close="closePlayer"
      @stop="stopPlayback"
      @transcribed="onTranscribed"
    />
  </div>
</template>

<style scoped>
.query-page {
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

.form-actions-row .search-history {
  margin-top: 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
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
  transition: all 0.2s;
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

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px var(--accent-glow);
}

.btn-primary:disabled {
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
  margin-right: 8px;
  vertical-align: middle;
}

.spinner.small {
  width: 14px;
  height: 14px;
  margin-right: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.results-section {
  margin-top: 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.result-count {
  color: var(--text-secondary);
  font-size: 13px;
}

.info-message {
  margin: 16px 24px;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 13px;
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
  letter-spacing: 0.5px;
}

.results-table td {
  font-size: 13px;
}

.results-table tr:hover td {
  background: var(--bg-tertiary);
}

.col-checkbox {
  width: 40px;
  text-align: center;
}

.results-table th.col-checkbox {
  width: 40px;
}

.col-checkbox input {
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.results-table .mono {
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-download {
  padding: 8px 16px;
  min-width: 80px;
  background: var(--bg-tertiary);
  border: 1px solid var(--accent-primary);
  border-radius: 6px;
  color: var(--accent-primary);
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-download:hover {
  background: var(--accent-primary);
  color: white;
}

.btn-download:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-play {
  padding: 8px 16px;
  min-width: 80px;
  background: var(--accent-primary);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-play:hover {
  background: var(--accent-secondary);
}

.btn-delete {
  padding: 8px 16px;
  min-width: 70px;
  background: var(--danger);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  font-family: var(--font-display);
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.btn-delete:hover {
  background: var(--danger-hover);
}

.transcribed-yes {
  color: #22c55e;
  font-weight: 600;
}

.transcribed-no {
  color: #9ca3af;
}

.bulk-actions {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 12px 16px;
  background: var(--bg-tertiary);
  border-radius: 0 0 8px 8px;
  margin-top: -8px;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-top: 1px solid var(--border-color);
}

.page-btn {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-primary);
  cursor: pointer;
  font-size: 12px;
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn.active {
  background: var(--accent-primary);
  color: white;
  border-color: var(--accent-primary);
}

.page-info {
  font-size: 13px;
  color: var(--text-secondary);
}

.btn-delete-all {
  padding: 8px 16px;
  background: var(--danger);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 8px;
}

.btn-delete-all:hover {
  background: var(--danger-hover);
}
</style>
