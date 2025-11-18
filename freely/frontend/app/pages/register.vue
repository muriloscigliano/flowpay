<template>
  <div class="min-h-screen flex items-center justify-center bg-background px-4">
    <div class="w-full max-w-md">
      <!-- Card -->
      <div class="bg-card rounded-4xl shadow-lg p-8 border border-border">
        <!-- Header -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-foreground mb-2">
            Create Account
          </h1>
          <p class="text-muted-foreground">
            Get started with Freely today
          </p>
        </div>

        <!-- Error Alert -->
        <div
          v-if="authError"
          class="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg"
        >
          <p class="text-sm text-destructive">{{ authError }}</p>
        </div>

        <!-- Register Form -->
        <form @submit.prevent="handleRegister" class="space-y-6">
          <!-- Email Field -->
          <div>
            <label
              for="email"
              class="block text-sm font-medium text-foreground mb-2"
            >
              Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              autocomplete="email"
              class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground transition-all"
              placeholder="you@example.com"
            />
          </div>

          <!-- Username Field -->
          <div>
            <label
              for="username"
              class="block text-sm font-medium text-foreground mb-2"
            >
              Username (optional)
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              autocomplete="username"
              class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground transition-all"
              placeholder="johndoe"
            />
          </div>

          <!-- Password Field -->
          <div>
            <label
              for="password"
              class="block text-sm font-medium text-foreground mb-2"
            >
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              autocomplete="new-password"
              minlength="8"
              class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground transition-all"
              placeholder="Minimum 8 characters"
            />
            <p class="mt-1 text-xs text-muted-foreground">
              Must be at least 8 characters long
            </p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="authLoading"
            class="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            <span v-if="!authLoading">Create Account</span>
            <span v-else class="flex items-center justify-center">
              <svg
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary-foreground"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Creating account...
            </span>
          </button>
        </form>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <p class="text-sm text-muted-foreground">
            Already have an account?
            <NuxtLink
              to="/login"
              class="text-primary hover:text-primary/80 font-medium transition-colors"
            >
              Sign in
            </NuxtLink>
          </p>
        </div>
      </div>

      <!-- Footer -->
      <p class="mt-8 text-center text-xs text-muted-foreground">
        By creating an account, you agree to our Terms of Service and Privacy Policy
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { register, error: authError, loading: authLoading, clearError } = useAuth()
const router = useRouter()

const form = reactive({
  email: '',
  username: '',
  password: '',
})

// Clear error when form changes
watch(form, () => {
  if (authError.value) {
    clearError()
  }
})

const handleRegister = async () => {
  const success = await register({
    email: form.email,
    password: form.password,
    username: form.username || undefined,
  })

  if (success) {
    // Redirect to chat page after successful registration
    await router.push('/chat')
  }
}

// Set page meta
definePageMeta({
  layout: false, // No layout for register page
})
</script>
