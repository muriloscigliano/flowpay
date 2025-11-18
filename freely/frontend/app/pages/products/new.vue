<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink
            to="/products"
            class="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <svg class="w-5 h-5 text-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </NuxtLink>
          <div>
            <h1 class="text-2xl font-bold text-foreground">Add New Product</h1>
            <p class="text-sm text-muted-foreground">Fill in the details below</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-card rounded-4xl shadow-lg border border-border p-8">
        <!-- Error Alert -->
        <div
          v-if="productsError"
          class="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg"
        >
          <p class="text-sm text-destructive">{{ productsError }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Basic Info Section -->
          <div class="space-y-4">
            <h2 class="text-lg font-semibold text-foreground">Basic Information</h2>

            <!-- Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-foreground mb-2">
                Product Name *
              </label>
              <input
                id="name"
                v-model="form.name"
                type="text"
                required
                class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                placeholder="e.g., Premium Coffee Beans"
                @input="generateSlug"
              />
            </div>

            <!-- Slug -->
            <div>
              <label for="slug" class="block text-sm font-medium text-foreground mb-2">
                Slug * (URL-friendly name)
              </label>
              <input
                id="slug"
                v-model="form.slug"
                type="text"
                required
                pattern="[a-z0-9-]+"
                class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground font-mono"
                placeholder="premium-coffee-beans"
              />
              <p class="mt-1 text-xs text-muted-foreground">
                Lowercase letters, numbers, and hyphens only
              </p>
            </div>

            <!-- Description -->
            <div>
              <label for="description" class="block text-sm font-medium text-foreground mb-2">
                Description
              </label>
              <textarea
                id="description"
                v-model="form.description"
                rows="4"
                class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                placeholder="Describe your product..."
              ></textarea>
            </div>
          </div>

          <!-- Pricing Section -->
          <div class="space-y-4 pt-6 border-t border-border">
            <h2 class="text-lg font-semibold text-foreground">Pricing</h2>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Price -->
              <div>
                <label for="price" class="block text-sm font-medium text-foreground mb-2">
                  Price ($) *
                </label>
                <input
                  id="price"
                  v-model="priceDisplay"
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                  placeholder="19.99"
                />
              </div>

              <!-- Currency -->
              <div>
                <label for="currency" class="block text-sm font-medium text-foreground mb-2">
                  Currency
                </label>
                <select
                  id="currency"
                  v-model="form.currency"
                  class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Inventory Section -->
          <div class="space-y-4 pt-6 border-t border-border">
            <h2 class="text-lg font-semibold text-foreground">Inventory</h2>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <!-- Stock -->
              <div>
                <label for="stock" class="block text-sm font-medium text-foreground mb-2">
                  Stock Available
                </label>
                <input
                  id="stock"
                  v-model="stockDisplay"
                  type="number"
                  min="0"
                  class="w-full px-4 py-3 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
                  placeholder="Leave empty for unlimited"
                />
                <p class="mt-1 text-xs text-muted-foreground">
                  Leave empty for unlimited stock
                </p>
              </div>

              <!-- Checkboxes -->
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    v-model="form.is_available"
                    type="checkbox"
                    class="w-5 h-5 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                  />
                  <span class="text-sm text-foreground">Product is available for sale</span>
                </label>

                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    v-model="form.is_digital"
                    type="checkbox"
                    class="w-5 h-5 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                  />
                  <span class="text-sm text-foreground">This is a digital product</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Categories Section -->
          <div class="space-y-4 pt-6 border-t border-border">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-semibold text-foreground">Categories</h2>
              <button
                type="button"
                class="text-sm text-primary hover:text-primary/80"
                @click="showCategoryModal = true"
              >
                + Add Category
              </button>
            </div>

            <div v-if="categories && categories.length > 0" class="flex flex-wrap gap-3">
              <label
                v-for="category in categories"
                :key="category.id"
                class="flex items-center gap-2 px-4 py-2 bg-background border border-input rounded-lg cursor-pointer hover:border-primary transition-colors"
              >
                <input
                  v-model="form.category_ids"
                  type="checkbox"
                  :value="category.id"
                  class="w-4 h-4 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                />
                <span class="text-sm text-foreground">{{ category.name }}</span>
              </label>
            </div>
            <p v-else class="text-sm text-muted-foreground">
              No categories yet. Create one to organize your products.
            </p>
          </div>

          <!-- Form Actions -->
          <div class="pt-6 border-t border-border flex gap-3">
            <button
              type="submit"
              :disabled="productsLoading"
              class="flex-1 py-3 px-6 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <span v-if="!productsLoading">Create Product</span>
              <span v-else class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating...
              </span>
            </button>

            <NuxtLink
              to="/products"
              class="px-6 py-3 bg-background border border-border text-foreground font-medium rounded-lg hover:bg-muted transition-all text-center"
            >
              Cancel
            </NuxtLink>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const { categories, loading: productsLoading, error: productsError, createProduct, fetchCategories } = useProducts()
const router = useRouter()

const form = reactive({
  name: '',
  slug: '',
  description: '',
  price_cents: 0,
  currency: 'USD',
  stock_available: null as number | null,
  is_available: true,
  is_digital: false,
  category_ids: [] as string[],
})

const priceDisplay = ref('')
const stockDisplay = ref('')
const showCategoryModal = ref(false)

// Fetch categories on mount
onMounted(async () => {
  await fetchCategories()
})

// Generate slug from name
const generateSlug = () => {
  if (!form.slug) {
    form.slug = form.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }
}

// Watch price display and convert to cents
watch(priceDisplay, (value) => {
  const price = parseFloat(value) || 0
  form.price_cents = Math.round(price * 100)
})

// Watch stock display
watch(stockDisplay, (value) => {
  form.stock_available = value ? parseInt(value) : null
})

const handleSubmit = async () => {
  const product = await createProduct({
    name: form.name,
    slug: form.slug,
    description: form.description || undefined,
    price_cents: form.price_cents,
    currency: form.currency,
    stock_available: form.stock_available,
    is_available: form.is_available,
    is_digital: form.is_digital,
    category_ids: form.category_ids.length > 0 ? form.category_ids : undefined,
  })

  if (product) {
    await router.push('/products')
  }
}

definePageMeta({
  layout: false,
  middleware: 'auth',
})
</script>
