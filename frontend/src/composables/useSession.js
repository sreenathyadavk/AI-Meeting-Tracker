// composables/useSession.js
import { ref, onBeforeUnmount } from 'vue'

const sessionId = ref(null)
const API_BASE = 'http://localhost:8000'

export function useSession() {
    // Generate session ID
    const initSession = () => {
        if (!sessionId.value) {
            sessionId.value = crypto.randomUUID()
        }
        return sessionId.value
    }

    // Cleanup session
    const cleanupSession = async () => {
        if (sessionId.value) {
            try {
                await fetch(`${API_BASE}/api/cleanup?session_id=${sessionId.value}`, {
                    method: 'POST'
                })
                console.log('Session cleaned up')
            } catch (err) {
                console.error('Cleanup failed:', err)
            }
        }
    }

    // Register cleanup on page unload
    if (typeof window !== 'undefined') {
        window.addEventListener('beforeunload', cleanupSession)
    }

    // Also cleanup on component unmount
    onBeforeUnmount(cleanupSession)

    return {
        sessionId: sessionId.value || initSession(),
        cleanupSession
    }
}
