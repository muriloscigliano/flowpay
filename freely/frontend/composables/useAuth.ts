/**
 * Authentication composable for Freely
 * Manages user authentication state and operations
 */

import type { Ref } from 'vue'

export interface User {
  id: string
  email: string
  username: string | null
  avatar_url: string | null
  is_admin: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  username?: string
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const user = useState<User | null>('auth:user', () => null)
  const loading = useState<boolean>('auth:loading', () => false)
  const error = useState<string | null>('auth:error', () => null)

  const apiUrl = config.public.apiUrl

  /**
   * Register a new user
   */
  const register = async (data: RegisterRequest): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<User>(`${apiUrl}/v1/auth/register`, {
        method: 'POST',
        body: data,
        credentials: 'include',
      })

      user.value = response
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Login with email and password
   */
  const login = async (data: LoginRequest): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<User>(`${apiUrl}/v1/auth/login`, {
        method: 'POST',
        body: data,
        credentials: 'include',
      })

      user.value = response
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Logout current user
   */
  const logout = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(`${apiUrl}/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      })

      user.value = null
    } catch (e: any) {
      error.value = e.data?.detail || 'Logout failed'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch current authenticated user
   */
  const fetchUser = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<User>(`${apiUrl}/v1/auth/me`, {
        method: 'GET',
        credentials: 'include',
      })

      user.value = response
    } catch (e: any) {
      user.value = null
      error.value = e.data?.detail || 'Failed to fetch user'
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }

  return {
    user: readonly(user),
    loading: readonly(loading),
    error: readonly(error),
    authenticated: computed(() => !!user.value),
    register,
    login,
    logout,
    fetchUser,
    clearError,
  }
}
