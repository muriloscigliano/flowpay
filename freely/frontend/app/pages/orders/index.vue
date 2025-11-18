<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-foreground">My Orders</h1>
          <p class="text-sm text-muted-foreground">View and track your order history</p>
        </div>
        <div class="flex items-center gap-3">
          <NuxtLink to="/products" class="text-sm text-primary hover:text-primary/80">
            Continue Shopping
          </NuxtLink>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 py-8">
      <!-- Loading State -->
      <div v-if="loading && orders.length === 0" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-muted-foreground">Loading orders...</p>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!loading && orders.length === 0"
        class="text-center py-12 bg-card rounded-4xl border border-border"
      >
        <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">No orders yet</h3>
        <p class="text-muted-foreground mb-6">Start shopping to see your orders here</p>
        <NuxtLink
          to="/products"
          class="inline-block px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90"
        >
          Browse Products
        </NuxtLink>
      </div>

      <!-- Orders List -->
      <div v-else class="space-y-4">
        <div
          v-for="order in orders"
          :key="order.id"
          class="bg-card rounded-2xl border border-border p-6 hover:shadow-lg transition-shadow cursor-pointer"
          @click="navigateTo(`/orders/${order.id}`)"
        >
          <!-- Order Header -->
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="font-semibold text-foreground">Order {{ order.order_number }}</h3>
              <p class="text-sm text-muted-foreground">
                {{ formatDate(order.created_at) }}
              </p>
            </div>
            <div class="text-right">
              <div class="text-lg font-bold text-foreground">{{ order.total_display }}</div>
              <div class="text-sm text-muted-foreground">{{ order.items.length }} item{{ order.items.length !== 1 ? 's' : '' }}</div>
            </div>
          </div>

          <!-- Status Badges -->
          <div class="flex gap-2 mb-4">
            <span
              :class="[
                'px-3 py-1 text-xs font-medium rounded-full',
                getPaymentStatusDisplay(order.payment_status).color,
              ]"
            >
              {{ getPaymentStatusDisplay(order.payment_status).text }}
            </span>
            <span
              :class="[
                'px-3 py-1 text-xs font-medium rounded-full',
                getFulfillmentStatusDisplay(order.fulfillment_status).color,
              ]"
            >
              {{ getFulfillmentStatusDisplay(order.fulfillment_status).text }}
            </span>
          </div>

          <!-- Order Items Preview -->
          <div class="space-y-2">
            <div
              v-for="item in order.items.slice(0, 3)"
              :key="item.id"
              class="flex items-center justify-between text-sm"
            >
              <span class="text-foreground">
                {{ item.quantity }}x {{ item.product_name }}
              </span>
              <span class="text-muted-foreground">{{ item.subtotal_display }}</span>
            </div>
            <div v-if="order.items.length > 3" class="text-sm text-muted-foreground">
              +{{ order.items.length - 3 }} more item{{ order.items.length - 3 !== 1 ? 's' : '' }}
            </div>
          </div>

          <!-- View Details Link -->
          <div class="mt-4 pt-4 border-t border-border">
            <span class="text-sm text-primary hover:text-primary/80 font-medium">
              View Order Details →
            </span>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalOrders > pageSize" class="mt-8 flex items-center justify-center gap-2">
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
  orders,
  loading,
  total: totalOrders,
  page: currentPage,
  pageSize,
  fetchOrders,
  getPaymentStatusDisplay,
  getFulfillmentStatusDisplay,
} = useOrders()

const totalPages = computed(() => Math.ceil(totalOrders.value / pageSize.value))

// Fetch orders on mount
onMounted(async () => {
  await fetchOrders()
})

// Handle page change
const changePage = async (page: number) => {
  await fetchOrders({ page })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Format date
const formatDate = (timestamp: string): string => {
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

definePageMeta({
  layout: false,
  middleware: 'auth',
})
</script>
