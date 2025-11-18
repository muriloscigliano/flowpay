/**
 * Auth middleware - Protects routes that require authentication
 */

export default defineNuxtRouteMiddleware(async (to, from) => {
  const { authenticated, fetchUser } = useAuth()

  // Try to fetch user if not already authenticated
  if (!authenticated.value) {
    await fetchUser()
  }

  // Redirect to login if still not authenticated
  if (!authenticated.value) {
    return navigateTo('/login')
  }
})
