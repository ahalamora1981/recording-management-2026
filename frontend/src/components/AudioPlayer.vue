<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'
import { useI18n } from '../composables/useI18n'
import appConfig from '../config.js'

const props = defineProps({
  show: Boolean,
  recording: Object,
  ccrdId: String,
  autoTranscribe: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'stop', 'transcribed'])

const { t } = useI18n()
const API_URL = appConfig.apiUrl

const isPlaying = ref(false)
const isPaused = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const isLoading = ref(false)
const isTranscribing = ref(false)
const transcription = ref('')
const fileMissing = ref(false)
let audio = null

watch(() => props.show, async (newVal) => {
  if (newVal && props.ccrdId) {
    transcription.value = ''
    fileMissing.value = false
    await initAudio()
    await loadTranscription()
  }
})

async function loadTranscription() {
  const hasExistingTranscription = props.recording?.transcribed === 'Yes'
  
  if (!hasExistingTranscription && !props.autoTranscribe) {
    return
  }
  
  isTranscribing.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(
      `${API_URL}/recordings/${props.ccrdId}/transcribe`,
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    )
    transcription.value = response.data.transcription || ''
    emit('transcribed', { ccrdId: props.ccrdId, transcription: transcription.value })
  } catch (e) {
    if (e.response?.status === 404 || e.response?.data?.detail?.includes('not found')) {
      fileMissing.value = true
    }
    console.error('Failed to transcribe:', e)
    transcription.value = ''
  } finally {
    isTranscribing.value = false
  }
}

async function initAudio() {
  if (audio) {
    audio.pause()
    audio = null
  }
  
  isLoading.value = true
  fileMissing.value = false
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get(`${API_URL}/download/${props.ccrdId}`, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${token}` }
    })
    
    const blob = new Blob([response.data], { type: 'audio/mpeg' })
    const url = URL.createObjectURL(blob)
    
    audio = new Audio(url)
    audio.addEventListener('loadedmetadata', () => {
      if (!audio) return
      duration.value = audio.duration
    })
    audio.addEventListener('timeupdate', () => {
      if (!audio) return
      currentTime.value = audio.currentTime
    })
    audio.addEventListener('ended', () => {
      if (!audio) return
      isPlaying.value = false
      isPaused.value = false
      currentTime.value = 0
    })
  } catch (e) {
    if (e.response?.status === 404 || e.response?.data?.detail?.includes('not found')) {
      fileMissing.value = true
    }
    console.error('Failed to load audio:', e)
  } finally {
    isLoading.value = false
  }
}

function togglePlay() {
  if (!audio) return
  if (isPlaying.value && !isPaused.value) {
    audio.pause()
    isPaused.value = true
  } else if (isPaused.value) {
    audio.play()
    isPaused.value = false
  } else {
    audio.play()
    isPlaying.value = true
  }
}

function stop() {
  if (!audio) return
  audio.pause()
  audio.currentTime = 0
  isPlaying.value = false
  isPaused.value = false
  currentTime.value = 0
  emit('stop')
}

function closeModal() {
  if (audio) {
    audio.pause()
    audio.src = ''
    audio = null
  }
  isPlaying.value = false
  isPaused.value = false
  currentTime.value = 0
  emit('close')
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
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

function handleSeek(event) {
  if (!audio) return
  const rect = event.currentTarget.getBoundingClientRect()
  const percent = (event.clientX - rect.left) / rect.width
  audio.currentTime = percent * duration.value
}
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click.self="closeModal">
      <div class="player-modal">
        <div class="modal-header">
          <h3>{{ t('player.title') }}</h3>
          <button class="close-btn" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="recording-info">
          <div class="info-item">
            <span class="label">{{ t('player.userName') }}</span>
            <span class="value">{{ recording?.verba_user_name || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ t('player.startTime') }}</span>
            <span class="value">{{ formatDateTime(recording?.start_time) }}</span>
          </div>
          <div class="info-item">
            <span class="label">{{ t('player.duration') }}</span>
            <span class="value">{{ formatTime(duration) }}</span>
          </div>
        </div>
        
        <div class="progress-container">
          <div class="progress-bar" @click="handleSeek">
            <div class="progress-fill" :style="{ width: (currentTime / duration * 100) + '%' }"></div>
          </div>
          <div class="time-display">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>
        </div>
        
        <div class="transcription-section">
          <div class="transcription-header">
            <span class="label">{{ t('player.transcription') || 'Transcription' }}</span>
            <span v-if="isTranscribing" class="transcribing-indicator">{{ t('player.transcribing') || 'Transcribing...' }}</span>
          </div>
          <div class="transcription-content">
            <template v-if="fileMissing">
              <span class="no-transcription" style="color: var(--danger);">Recording file not found - cannot transcribe</span>
            </template>
            <template v-else-if="transcription">{{ transcription }}</template>
            <template v-else-if="!isTranscribing && !transcription">
              <span class="no-transcription">{{ t('player.noTranscription') || 'No transcription available' }}</span>
            </template>
          </div>
        </div>
        
        <div class="controls">
          <button class="control-btn" @click="togglePlay">
            <svg v-if="!isPlaying || isPaused" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="4" width="4" height="16"/>
              <rect x="14" y="4" width="4" height="16"/>
            </svg>
            <span>{{ !isPlaying ? t('player.play') : (isPaused ? t('player.resume') : t('player.pause')) }}</span>
          </button>
          
          <button class="control-btn stop" @click="stop">
            <svg viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12"/>
            </svg>
            <span>{{ t('player.stop') }}</span>
          </button>
          
          <button class="control-btn quit" @click="closeModal">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
            <span>{{ t('player.quit') }}</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.player-modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  padding: 24px;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: var(--bg-tertiary);
}

.close-btn svg {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
}

.recording-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  background: var(--bg-tertiary);
  padding: 16px;
  border-radius: 10px;
}

.info-item .label {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.info-item .value {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.progress-container {
  margin-bottom: 24px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 4px;
  transition: width 0.1s linear;
}

.time-display {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}

.controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn svg {
  width: 18px;
  height: 18px;
}

.control-btn:not(.quit):not(.stop) {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
}

.control-btn:not(.quit):not(.stop):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--accent-glow);
}

.control-btn.stop {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.control-btn.stop:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.control-btn.quit {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.control-btn.quit:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.transcription-section {
  margin-bottom: 24px;
  background: var(--bg-tertiary);
  border-radius: 10px;
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.transcription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.transcription-header .label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.transcribing-indicator {
  font-size: 12px;
  color: var(--accent-primary);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.transcription-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.no-transcription {
  color: var(--text-muted);
  font-style: italic;
}
</style>
