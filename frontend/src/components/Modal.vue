<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

const showModal = ref(false)
const modalConfig = ref({
  title: '',
  message: '',
  type: 'info',
  confirmText: '',
  cancelText: '',
  onConfirm: null,
  onCancel: null
})

function openModal(config) {
  modalConfig.value = {
    title: config.title || '',
    message: config.message || '',
    type: config.type || 'info',
    confirmText: config.confirmText || '',
    cancelText: config.cancelText || '',
    onConfirm: config.onConfirm || null,
    onCancel: config.onCancel || null
  }
  showModal.value = true
}

const confirmButtonText = computed(() => modalConfig.value.confirmText || t('common.confirm'))
const cancelButtonText = computed(() => modalConfig.value.cancelText || t('common.cancel'))

function closeModal() {
  if (modalConfig.value.onCancel) {
    modalConfig.value.onCancel()
  }
  showModal.value = false
}

function confirm() {
  if (modalConfig.value.onConfirm) {
    modalConfig.value.onConfirm()
  }
  showModal.value = false
}

function alert(message, title = 'Notice') {
  return new Promise((resolve) => {
    openModal({
      title,
      message,
      type: 'alert',
      confirmText: 'OK',
      cancelText: '',
      onConfirm: resolve
    })
  })
}

function confirmDialog(message, title = 'Confirm') {
  return new Promise((resolve, reject) => {
    openModal({
      title,
      message,
      type: 'confirm',
      onConfirm: () => resolve(true),
      onCancel: () => reject(new Error('Cancelled'))
    })
  })
}

defineExpose({ openModal, alert, confirmDialog })
</script>

<template>
  <Teleport to="body">
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <span class="modal-title">{{ modalConfig.title }}</span>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          {{ modalConfig.message }}
        </div>
        <div class="modal-footer">
          <button 
            v-if="modalConfig.type === 'confirm'" 
            class="btn-modal btn-cancel" 
            @click="closeModal"
          >
            {{ cancelButtonText }}
          </button>
          <button 
            class="btn-modal" 
            :class="(modalConfig.type === 'danger' || modalConfig.type === 'confirm') ? 'btn-danger' : 'btn-confirm'" 
            @click="confirm"
          >
            {{ confirmButtonText }}
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
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-container {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  animation: slideIn 0.25s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.modal-close:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 20px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.btn-modal {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-confirm {
  background: var(--accent-primary);
  color: white;
}

.btn-confirm:hover {
  background: var(--accent-secondary);
}

.btn-danger {
  background: var(--danger);
  color: white;
}

.btn-danger:hover {
  background: var(--danger-hover);
}

.btn-cancel {
  background: var(--bg-tertiary);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-cancel:hover {
  border-color: var(--text-muted);
}
</style>
