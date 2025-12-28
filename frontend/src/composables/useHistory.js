// composables/useHistory.js
import { ref, watch } from 'vue'

const HISTORY_KEY = 'meeting_history'

export function useHistory() {
    const history = ref([])

    // Load from localStorage
    const loadHistory = () => {
        try {
            const stored = localStorage.getItem(HISTORY_KEY)
            if (stored) {
                history.value = JSON.parse(stored)
            }
        } catch (err) {
            console.error('Failed to load history:', err)
        }
    }

    // Save to localStorage
    const saveHistory = () => {
        try {
            localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value))
        } catch (err) {
            console.error('Failed to save history:', err)
        }
    }

    // Add new meeting to history
    const addToHistory = (meeting) => {
        history.value.unshift({
            ...meeting,
            id: Date.now(),
            timestamp: new Date().toISOString()
        })

        // Keep only last 10
        if (history.value.length > 10) {
            history.value = history.value.slice(0, 10)
        }

        saveHistory()
    }

    // Remove from history
    const removeFromHistory = (id) => {
        history.value = history.value.filter(item => item.id !== id)
        saveHistory()
    }

    // Clear all history
    const clearHistory = () => {
        history.value = []
        localStorage.removeItem(HISTORY_KEY)
    }

    // Auto-save when history changes
    watch(history, saveHistory, { deep: true })

    return {
        history,
        loadHistory,
        addToHistory,
        removeFromHistory,
        clearHistory
    }
}
