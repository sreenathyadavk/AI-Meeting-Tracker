<template>
  <div v-if="loading" class="card text-center">
    <div class="spinner mb-1"></div>
    <h3>Loading results...</h3>
  </div>

  <div v-else-if="results" class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
      <h2>📋 Extracted Tasks ({{ results.task_count }})</h2>
      <router-link to="/" class="btn btn-primary" style="text-decoration: none;">
        ⬅️ New Upload
      </router-link>
    </div>
    
    <!-- Tasks -->
    <div v-if="results.tasks.length > 0">
      <div v-for="(task, index) in results.tasks" :key="index" class="task-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
          <h4 style="flex: 1; margin-right: 1rem;">{{ task.task }}</h4>
          <span 
            class="confidence-badge"
            :class="getConfidenceClass(task.confidence)"
          >
            {{ (task.confidence * 100).toFixed(0) }}%
          </span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.9rem;">
          <div>
            <span class="text-muted">Owner:</span> 
            <strong>{{ task.owner }}</strong>
          </div>
          <div>
            <span class="text-muted">Deadline:</span> 
            <strong>{{ task.deadline }}</strong>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center" style="padding: 2rem;">
      <p class="text-muted">No tasks found in this recording.</p>
    </div>

    <!-- Transcript -->
    <details style="margin-top: 1.5rem;">
      <summary style="cursor: pointer; font-weight: 600; margin-bottom: 1rem;">
        📝 View Full Transcript
      </summary>
      <div style="background: var(--color-bg); padding: 1rem; border-radius: var(--radius-sm); max-height: 300px; overflow-y: auto;">
        <p style="white-space: pre-wrap; line-height: 1.8;">{{ results.transcript }}</p>
      </div>
    </details>

    <!-- Chat Section -->
    <div class="chat-section mt-2">
      <h3 style="margin-bottom: 1rem;">💬 Ask About This Meeting</h3>
      
      <div class="chat-messages" v-if="chatHistory.length > 0" style="max-height: 300px; overflow-y: auto; margin-bottom: 1rem;">
        <div v-for="(msg, index) in chatHistory" :key="index" style="margin-bottom: 1rem;">
          <div style="background: var(--color-bg); padding: 0.75rem; border-radius: var(--radius-sm); margin-bottom: 0.5rem;">
            <strong style="color: var(--color-primary);">You:</strong> {{ msg.question }}
          </div>
          <div style="background: var(--color-surface-light); padding: 0.75rem; border-radius: var(--radius-sm);">
            <strong style="color: var(--color-accent);">AI:</strong> {{ msg.answer }}
          </div>
        </div>
      </div>

      <div style="display: flex; gap: 0.5rem;">
        <input
          v-model="chatQuestion"
          @keyup.enter="askQuestion"
          type="text"
          placeholder="Ask a question about the meeting..."
          style="flex: 1; padding: 0.75rem; background: var(--color-bg); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--radius-sm); color: var(--color-text);"
          :disabled="chatLoading"
        />
        <button
          @click="askQuestion"
          class="btn btn-primary"
          :disabled="!chatQuestion.trim() || chatLoading"
          style="min-width: 100px;"
        >
          {{ chatLoading ? '...' : 'Ask' }}
        </button>
      </div>
    </div>
  </div>

  <div v-else class="card">
    <div class="text-center" style="padding: 2rem;">
      <div style="font-size: 3rem; margin-bottom: 1rem;">🗂️</div>
      <h3 style="margin-bottom: 0.5rem;">Meeting Not Available</h3>
      <p class="text-muted" style="margin-bottom: 1.5rem;">
        Audio files are automatically cleaned up for privacy.<br/>
        Please upload the recording again to view results.
      </p>
      <router-link to="/" class="btn btn-primary" style="text-decoration: none;">
        ⬅️ Upload New Recording
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const loading = ref(true)
const results = ref(null)
const chatQuestion = ref('')
const chatHistory = ref([])
const chatLoading = ref(false)

const API_BASE = 'http://localhost:8000'

onMounted(async () => {
  // Check if results came through route state (from fresh upload)
  if (history.state && history.state.results) {
    results.value = history.state.results
    loading.value = false
    return
  }
  
  // Otherwise, this is a history item click - don't have results
  // Show message to re-upload (file was cleaned up)
  loading.value = false
})

function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return 'confidence-high'
  if (confidence >= 0.5) return 'confidence-medium'
  return 'confidence-low'
}

async function askQuestion() {
  if (!chatQuestion.value.trim() || !results.value) return
  
  chatLoading.value = true
  
  try {
    const response = await fetch(`${API_BASE}/api/chat?question=${encodeURIComponent(chatQuestion.value)}&transcript=${encodeURIComponent(results.value.transcript)}`, {
      method: 'POST'
    })
    
    if (!response.ok) {
      throw new Error('Chat request failed')
    }
    
    const data = await response.json()
    
    chatHistory.value.push({
      question: chatQuestion.value,
      answer: data.answer
    })
    
    chatQuestion.value = ''
    
  } catch (err) {
    console.error('Chat error:', err)
  } finally {
    chatLoading.value = false
  }
}
</script>
