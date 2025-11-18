<template>
  <div class="min-h-screen flex items-center justify-center bg-background">
    <div class="text-center">
      <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg class="w-10 h-10 text-primary animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <p class="text-muted-foreground">Loading...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { authenticated, fetchUser } = useAuth()
const router = useRouter()

onMounted(async () => {
  // Try to fetch user
  await fetchUser()

  // Redirect based on auth status
  if (authenticated.value) {
    await router.push('/chat')
  } else {
    await router.push('/login')
  }
})

definePageMeta({
  layout: false,
})
</script>
