<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <span class="text-primary-foreground font-bold text-lg">F</span>
          </div>
          <div>
            <h1 class="text-lg font-semibold text-foreground">Freely AI</h1>
            <p class="text-xs text-muted-foreground">Your conversational commerce assistant</p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- User Menu -->
          <div v-if="user" class="flex items-center gap-3">
            <div class="text-right hidden sm:block">
              <p class="text-sm font-medium text-foreground">{{ user.username || user.email }}</p>
              <p class="text-xs text-muted-foreground">{{ user.email }}</p>
            </div>
            <button
              @click="handleLogout"
              class="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Chat Interface -->
    <main class="max-w-5xl mx-auto px-4 py-8">
      <!-- Chat Container -->
      <div class="bg-card rounded-4xl shadow-lg border border-border overflow-hidden" style="height: calc(100vh - 180px)">
        <!-- Messages Area -->
        <div ref="messagesContainer" class="h-full overflow-y-auto p-6 space-y-4">
          <!-- Welcome Message -->
          <div v-if="!currentConversation || currentConversation.messages.length === 0" class="flex items-center justify-center h-full">
            <div class="text-center max-w-md">
              <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
                </svg>
              </div>
              <h2 class="text-2xl font-bold text-foreground mb-2">Welcome to Freely AI</h2>
              <p class="text-muted-foreground mb-6">
                I'm here to help you find products, answer questions, and provide excellent customer service.
                Start a conversation below!
              </p>
            </div>
          </div>

          <!-- Messages -->
          <div v-else class="space-y-4">
            <div
              v-for="message in currentConversation.messages"
              :key="message.id"
              class="flex"
              :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[80%] rounded-2xl px-4 py-3"
                :class="
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-foreground'
                "
              >
                <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>
                <p class="text-xs mt-1 opacity-70">
                  {{ formatTime(message.created_at) }}
                </p>
              </div>
            </div>

            <!-- Sending Indicator -->
            <div v-if="sending" class="flex justify-start">
              <div class="bg-muted rounded-2xl px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="flex gap-1">
                    <div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                  <span class="text-xs text-muted-foreground">AI is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="border-t border-border p-4 bg-card">
          <!-- Error Display -->
          <div v-if="chatError" class="mb-3 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p class="text-sm text-destructive">{{ chatError }}</p>
          </div>

          <form @submit.prevent="handleSend" class="flex gap-3">
            <input
              v-model="messageInput"
              type="text"
              placeholder="Type your message..."
              :disabled="sending"
              class="flex-1 px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground disabled:opacity-50 transition-all"
            />
            <button
              type="submit"
              :disabled="!messageInput.trim() || sending"
              class="px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <svg v-if="!sending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const { user, authenticated, logout } = useAuth()
const { currentConversation, sending, error: chatError, sendMessage, clearError } = useChat()
const router = useRouter()

const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// Redirect if not authenticated
onMounted(async () => {
  if (!authenticated.value) {
    await router.push('/login')
  }
})

// Clear error when message input changes
watch(messageInput, () => {
  if (chatError.value) {
    clearError()
  }
})

// Auto-scroll to bottom when new messages arrive
watch(
  () => currentConversation.value?.messages,
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  },
  { deep: true }
)

const handleSend = async () => {
  if (!messageInput.value.trim() || sending.value) return

  const content = messageInput.value.trim()
  const conversationId = currentConversation.value?.id

  // Add user message to UI immediately
  if (currentConversation.value) {
    currentConversation.value.messages.push({
      id: `temp-${Date.now()}`,
      conversation_id: currentConversation.value.id,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    })
  }

  // Clear input
  messageInput.value = ''

  // Send to API
  await sendMessage(content, conversationId)
}

const handleLogout = async () => {
  await logout()
  await router.push('/login')
}

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`

  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Set page meta
definePageMeta({
  layout: false,
  middleware: 'auth', // We'll create this middleware
})
</script>
