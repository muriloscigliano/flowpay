<template>
  <div class="min-h-screen bg-background flex items-center justify-center px-4">
    <div class="max-w-2xl w-full">
      <!-- Success Card -->
      <div class="bg-card rounded-4xl shadow-lg border border-border p-8 text-center">
        <!-- Success Icon -->
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>

        <!-- Loading State -->
        <div v-if="loading && !currentOrder">
          <div class="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p class="text-muted-foreground">Loading order details...</p>
        </div>

        <!-- Order Confirmation -->
        <div v-else-if="currentOrder">
          <h1 class="text-3xl font-bold text-foreground mb-2">Order Confirmed!</h1>
          <p class="text-muted-foreground mb-8">
            Thank you for your purchase. Your order has been successfully placed.
          </p>

          <!-- Order Details -->
          <div class="bg-background rounded-2xl p-6 mb-6 text-left">
            <div class="flex items-center justify-between mb-4 pb-4 border-b border-border">
              <div>
                <p class="text-sm text-muted-foreground">Order Number</p>
                <p class="text-lg font-bold text-foreground">{{ currentOrder.order_number }}</p>
              </div>
              <div class="text-right">
                <p class="text-sm text-muted-foreground">Total</p>
                <p class="text-lg font-bold text-primary">{{ currentOrder.total_display }}</p>
              </div>
            </div>

            <div class="space-y-2">
              <div v-if="currentOrder.customer_email" class="flex justify-between text-sm">
                <span class="text-muted-foreground">Email:</span>
                <span class="text-foreground">{{ currentOrder.customer_email }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Date:</span>
                <span class="text-foreground">{{ formatDate(currentOrder.created_at) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Items:</span>
                <span class="text-foreground">{{ currentOrder.items.length }}</span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-3">
            <NuxtLink
              to="/orders"
              class="flex-1 py-3 px-6 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 transition-all text-center"
            >
              View All Orders
            </NuxtLink>
            <NuxtLink
              to="/products"
              class="flex-1 py-3 px-6 bg-background border border-border text-foreground font-medium rounded-lg hover:bg-muted transition-all text-center"
            >
              Continue Shopping
            </NuxtLink>
          </div>

          <!-- Info Message -->
          <p class="mt-6 text-xs text-muted-foreground">
            A confirmation email has been sent to {{ currentOrder.customer_email || 'your email' }}
          </p>
        </div>

        <!-- Error State -->
        <div v-else>
          <div class="w-20 h-20 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-10 h-10 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <h2 class="text-xl font-bold text-foreground mb-2">Order Not Found</h2>
          <p class="text-muted-foreground mb-6">We couldn't find your order. Please check your email for confirmation.</p>
          <NuxtLink
            to="/products"
            class="inline-block px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90"
          >
            Continue Shopping
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { currentOrder, loading, fetchOrderByNumber } = useOrders()

// Get order number from query parameter
const orderNumber = route.query.order_number as string

onMounted(async () => {
  if (orderNumber) {
    await fetchOrderByNumber(orderNumber)
  }
})

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
})
</script>
