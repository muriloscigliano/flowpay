/**
 * Chat composable for Freely
 * Manages conversations and messages with AI
 */

export interface Message {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
}

export interface Conversation {
  id: string
  title: string | null
  customer_email: string | null
  customer_name: string | null
  created_at: string
  messages: Message[]
}

export interface SendMessageRequest {
  content: string
  conversation_id?: string
}

export const useChat = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const conversations = useState<Conversation[]>('chat:conversations', () => [])
  const currentConversation = useState<Conversation | null>('chat:current', () => null)
  const loading = useState<boolean>('chat:loading', () => false)
  const sending = useState<boolean>('chat:sending', () => false)
  const error = useState<string | null>('chat:error', () => null)

  /**
   * Fetch all conversations
   */
  const fetchConversations = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Conversation[]>(`${apiUrl}/v1/chat/conversations`, {
        method: 'GET',
        credentials: 'include',
      })

      conversations.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch conversations'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch a specific conversation by ID
   */
  const fetchConversation = async (conversationId: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Conversation>(
        `${apiUrl}/v1/chat/conversations/${conversationId}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      )

      currentConversation.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch conversation'
    } finally {
      loading.value = false
    }
  }

  /**
   * Send a message and get AI response
   */
  const sendMessage = async (content: string, conversationId?: string): Promise<Message | null> => {
    sending.value = true
    error.value = null

    try {
      const response = await $fetch<Message>(`${apiUrl}/v1/chat/send`, {
        method: 'POST',
        body: {
          content,
          conversation_id: conversationId || null,
        },
        credentials: 'include',
      })

      // Update current conversation with new message
      if (currentConversation.value && currentConversation.value.id === response.conversation_id) {
        currentConversation.value.messages.push(response)
      } else if (!conversationId) {
        // New conversation created, fetch it
        await fetchConversation(response.conversation_id)
      }

      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to send message'
      return null
    } finally {
      sending.value = false
    }
  }

  /**
   * Create a new conversation
   */
  const createConversation = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Conversation>(`${apiUrl}/v1/chat/conversations`, {
        method: 'POST',
        body: {},
        credentials: 'include',
      })

      currentConversation.value = response
      conversations.value.unshift(response)
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to create conversation'
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear current conversation
   */
  const clearCurrentConversation = () => {
    currentConversation.value = null
  }

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }

  return {
    conversations: readonly(conversations),
    currentConversation: readonly(currentConversation),
    loading: readonly(loading),
    sending: readonly(sending),
    error: readonly(error),
    fetchConversations,
    fetchConversation,
    sendMessage,
    createConversation,
    clearCurrentConversation,
    clearError,
  }
}
