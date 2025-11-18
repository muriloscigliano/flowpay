<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-foreground">Products</h1>
          <p class="text-sm text-muted-foreground">Manage your product catalog</p>
        </div>

        <div class="flex items-center gap-3">
          <NuxtLink to="/cart" class="relative px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            <span>Cart</span>
            <span v-if="cartItemCount > 0" class="absolute -top-1 -right-1 w-5 h-5 bg-primary text-primary-foreground text-xs font-bold rounded-full flex items-center justify-center">
              {{ cartItemCount }}
            </span>
          </NuxtLink>
          <NuxtLink to="/orders" class="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            Orders
          </NuxtLink>
          <NuxtLink to="/chat" class="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
            Chat
          </NuxtLink>
          <NuxtLink to="/products/new" class="px-4 py-2 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-all">
            Add Product
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 py-8">
      <!-- Search and Filters -->
      <div class="mb-6 flex flex-col sm:flex-row gap-4">
        <!-- Search -->
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search products..."
          class="flex-1 px-4 py-3 bg-card border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground placeholder:text-muted-foreground"
          @input="handleSearch"
        />

        <!-- Category Filter -->
        <select
          v-model="selectedCategory"
          class="px-4 py-3 bg-card border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
          @change="handleFilter"
        >
          <option value="">All Categories</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>

        <!-- Availability Filter -->
        <select
          v-model="availabilityFilter"
          class="px-4 py-3 bg-card border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-foreground"
          @change="handleFilter"
        >
          <option value="">All Products</option>
          <option value="true">Available</option>
          <option value="false">Unavailable</option>
        </select>
      </div>

      <!-- Loading State -->
      <div v-if="productsLoading && products.length === 0" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-muted-foreground">Loading products...</p>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!productsLoading && products.length === 0"
        class="text-center py-12 bg-card rounded-4xl border border-border"
      >
        <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">No products yet</h3>
        <p class="text-muted-foreground mb-6">Get started by adding your first product</p>
        <NuxtLink
          to="/products/new"
          class="inline-block px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-all"
        >
          Add Product
        </NuxtLink>
      </div>

      <!-- Products Grid -->
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <div
          v-for="product in products"
          :key="product.id"
          class="bg-card rounded-4xl border border-border overflow-hidden hover:shadow-lg transition-shadow"
        >
          <!-- Product Image -->
          <div class="aspect-square bg-muted flex items-center justify-center cursor-pointer" @click="navigateTo(`/products/${product.id}`)">
            <img
              v-if="product.image_urls && product.image_urls[0]"
              :src="product.image_urls[0]"
              :alt="product.name"
              class="w-full h-full object-cover"
            />
            <svg
              v-else
              class="w-16 h-16 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              ></path>
            </svg>
          </div>

          <!-- Product Info -->
          <div class="p-4">
            <div class="flex items-start justify-between mb-2 cursor-pointer" @click="navigateTo(`/products/${product.id}`)">
              <h3 class="font-semibold text-foreground truncate flex-1">{{ product.name }}</h3>
              <span
                v-if="!product.is_available"
                class="ml-2 px-2 py-1 text-xs bg-destructive/10 text-destructive rounded"
              >
                Unavailable
              </span>
            </div>

            <p v-if="product.description" class="text-sm text-muted-foreground mb-3 line-clamp-2 cursor-pointer" @click="navigateTo(`/products/${product.id}`)">
              {{ product.description }}
            </p>

            <div class="flex items-center justify-between mb-3">
              <span class="text-lg font-bold text-primary">{{ product.price_display }}</span>
              <span v-if="product.stock_available !== null" class="text-xs text-muted-foreground">
                {{ product.stock_available }} in stock
              </span>
            </div>

            <!-- Add to Cart Button -->
            <button
              @click="handleAddToCart(product)"
              :disabled="!product.is_available || addingToCart === product.id"
              class="w-full py-2 px-4 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
            >
              <span v-if="addingToCart === product.id" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Adding...
              </span>
              <span v-else-if="!product.is_available">Out of Stock</span>
              <span v-else>Add to Cart</span>
            </button>

            <!-- Categories -->
            <div v-if="product.categories && product.categories.length > 0" class="mt-3 flex flex-wrap gap-2">
              <span
                v-for="category in product.categories.slice(0, 2)"
                :key="category.id"
                class="px-2 py-1 text-xs bg-muted text-muted-foreground rounded"
              >
                {{ category.name }}
              </span>
              <span
                v-if="product.categories.length > 2"
                class="px-2 py-1 text-xs bg-muted text-muted-foreground rounded"
              >
                +{{ product.categories.length - 2 }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div
        v-if="totalProducts > pageSize"
        class="mt-8 flex items-center justify-center gap-2"
      >
        <button
          :disabled="currentPage === 1"
          class="px-4 py-2 bg-card border border-border rounded-lg hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
          @click="changePage(currentPage - 1)"
        >
          Previous
        </button>

        <span class="px-4 py-2 text-muted-foreground">
          Page {{ currentPage }} of {{ totalPages }}
        </span>

        <button
          :disabled="currentPage === totalPages"
          class="px-4 py-2 bg-card border border-border rounded-lg hover:bg-muted disabled:opacity-50 disabled:cursor-not-allowed"
          @click="changePage(currentPage + 1)"
        >
          Next
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const {
  products,
  categories,
  loading: productsLoading,
  total: totalProducts,
  page: currentPage,
  pageSize,
  fetchProducts,
  fetchCategories,
} = useProducts()

const { addToCart, fetchCart, itemCount: cartItemCount } = useCart()

const searchQuery = ref('')
const selectedCategory = ref('')
const availabilityFilter = ref('')
const addingToCart = ref<string | null>(null)

const totalPages = computed(() => Math.ceil(totalProducts.value / pageSize.value))

// Fetch initial data
onMounted(async () => {
  await fetchCategories()
  await fetchProducts()
  await fetchCart()
})

// Handle add to cart
const handleAddToCart = async (product: any) => {
  addingToCart.value = product.id
  const success = await addToCart(product.id, 1)
  addingToCart.value = null

  if (success) {
    // Show success feedback (could be a toast notification)
    console.log(`Added ${product.name} to cart`)
  }
}

// Handle search with debounce
let searchTimeout: NodeJS.Timeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    handleFilter()
  }, 300)
}

// Handle filter changes
const handleFilter = async () => {
  await fetchProducts({
    search: searchQuery.value || undefined,
    categoryId: selectedCategory.value || undefined,
    isAvailable: availabilityFilter.value ? availabilityFilter.value === 'true' : undefined,
    page: 1,
  })
}

// Handle page change
const changePage = async (page: number) => {
  await fetchProducts({
    search: searchQuery.value || undefined,
    categoryId: selectedCategory.value || undefined,
    isAvailable: availabilityFilter.value ? availabilityFilter.value === 'true' : undefined,
    page,
  })

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Set page meta
definePageMeta({
  layout: false,
  middleware: 'auth',
})
</script>
