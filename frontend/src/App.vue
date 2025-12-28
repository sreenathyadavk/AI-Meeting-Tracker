<template>
  <div id="app">
    <header class="text-center mb-2">
      <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #6366f1, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
        🎙️ AI Meeting Tracker
      </h1>
      <p class="text-muted">Convert recordings to action items</p>
    </header>

    <div style="display: grid; grid-template-columns: 1fr 300px; gap: 1.5rem; max-width: 1200px; margin: 0 auto;">
      <!-- Main Content -->
      <div>
        <router-view @meeting-processed="handleMeetingProcessed" />
      </div>

      <!-- History Sidebar -->
      <div class="history-sidebar">
        <h3 style="margin-bottom: 1rem;">📚 History</h3>
        
        <div v-if="history.length === 0" class="text-muted text-center" style="padding: 2rem 0;">
          No meetings yet
        </div>
        
        <div v-else>
          <div 
            v-for="meeting in history" 
            :key="meeting.id"
            class="history-item"
            @click="$router.push(`/results/${meeting.filename}`)"
          >
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.25rem;">
              <strong style="font-size: 0.9rem;">{{ meeting.filename }}</strong>
              <button 
                @click.stop="removeFromHistory(meeting.id)"
                style="background: none; border: none; color: var(--color-error); cursor: pointer; padding: 0; font-size: 1.2rem;"
                title="Remove"
              >
                ×
              </button>
            </div>
            <p class="text-muted" style="font-size: 0.75rem; margin: 0;">
              {{ new Date(meeting.timestamp).toLocaleString() }}
            </p>
            <p class="text-muted" style="font-size: 0.75rem; margin: 0.25rem 0 0 0;">
              {{ meeting.taskCount }} tasks
            </p>
          </div>
          
          <button 
            @click="clearHistory"
            class="btn btn-primary mt-1"
            style="width: 100%; font-size: 0.85rem; padding: 0.5rem;"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useHistory } from './composables/useHistory'

const { history, loadHistory, addToHistory, removeFromHistory, clearHistory } = useHistory()

onMounted(() => {
  loadHistory()
})

function handleMeetingProcessed(meeting) {
  addToHistory(meeting)
}
</script>

<style>
.history-sidebar {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  height: fit-content;
  position: sticky;
  top: 1rem;
}

.history-item {
  background: var(--color-bg);
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.history-item:hover {
  border-color: var(--color-primary);
  transform: translateX(-2px);
}
</style>
