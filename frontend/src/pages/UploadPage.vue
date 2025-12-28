<template>
  <div class="card mb-2">
    <h2 style="margin-bottom: 1rem;">Upload Recording</h2>
    
    <div 
      class="upload-zone"
      :class="{ dragging: isDragging }"
      @click="triggerFileInput"
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
    >
      <div v-if="!selectedFile">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📁</div>
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">
          Drop your meeting recording here
        </p>
        <p class="text-muted" style="font-size: 0.9rem;">
          or click to browse (MP3, MP4, WAV, M4A)
        </p>
      </div>
      <div v-else>
        <div style="font-size: 3rem; margin-bottom: 1rem;">✅</div>
        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">
          {{ selectedFile.name }}
        </p>
        <p class="text-muted" style="font-size: 0.9rem;">
          {{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB
        </p>
      </div>
    </div>
    
    <input 
      ref="fileInput" 
      type="file" 
      accept=".mp3,.mp4,.wav,.m4a" 
      @change="handleFileSelect"
      style="display: none;"
    />
    
    <button 
      v-if="selectedFile"
      @click="processFile"
      class="btn btn-primary mt-2"
      style="width: 100%;"
      :disabled="processing"
    >
      {{ processing ? processingStatus : '🚀 Process Recording' }}
    </button>
  </div>

  <!-- Error Display -->
  <div v-if="error" class="card" style="border-left: 4px solid var(--color-error);">
    <h3 style="color: var(--color-error); margin-bottom: 0.5rem;">❌ Error</h3>
    <p>{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '../composables/useSession'

const router = useRouter()
const emit = defineEmits(['meeting-processed'])
const { sessionId } = useSession()

const fileInput = ref(null)
const selectedFile = ref(null)
const isDragging = ref(false)
const processing = ref(false)
const processingStatus = ref('')
const error = ref(null)

const API_BASE = 'http://localhost:8000'

function triggerFileInput() {
  fileInput.value.click()
}

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
  }
}

async function processFile() {
  if (!selectedFile.value) return
  
  error.value = null
  processing.value = true
  processingStatus.value = '📤 Uploading...'
  
  try {
    // Upload file
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const uploadResponse = await fetch(`${API_BASE}/api/upload`, {
      method: 'POST',
      body: formData
    })
    
    if (!uploadResponse.ok) {
      throw new Error('Upload failed')
    }
    
    const uploadData = await uploadResponse.json()
    
    // Process recording with session ID
    processingStatus.value = '🎙️ Transcribing...'
    
    const processResponse = await fetch(`${API_BASE}/api/process?filename=${encodeURIComponent(uploadData.filename)}&session_id=${sessionId}`, {
      method: 'POST'
    })
    
    if (!processResponse.ok) {
      throw new Error('Processing failed')
    }
    
    const processData = await processResponse.json()
    
    // Emit event for history
    emit('meeting-processed', {
      filename: uploadData.filename,
      taskCount: processData.task_count
    })
    
    // Navigate to results page WITH data (don't re-fetch)
    router.push({
      name: 'Results',
      params: { 
        filename: uploadData.filename 
      },
      state: {
        results: processData
      }
    })
    
  } catch (err) {
    console.error('Error:', err)
    error.value = err.message || 'An error occurred. Please try again.'
    processing.value = false
  }
}
</script>
