<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <NuxtLink to="/orders" class="p-2 hover:bg-muted rounded-lg transition-colors">
            <svg class="w-5 h-5 text-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </NuxtLink>
          <div>
            <h1 class="text-2xl font-bold text-foreground">
              Order {{ currentOrder?.order_number || '...' }}
            </h1>
            <p v-if="currentOrder" class="text-sm text-muted-foreground">
              Placed on {{ formatDate(currentOrder.created_at) }}
            </p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Loading State -->
      <div v-if="loading && !currentOrder" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-muted-foreground">Loading order...</p>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="text-center py-12 bg-card rounded-4xl border border-border"
      >
        <div class="w-20 h-20 bg-destructive/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-destructive" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">Order not found</h3>
        <p class="text-muted-foreground mb-6">{{ error }}</p>
        <NuxtLink to="/orders" class="inline-block px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90">
          Back to Orders
        </NuxtLink>
      </div>

      <!-- Order Details -->
      <div v-else-if="currentOrder" class="space-y-6">
        <!-- Status Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-card rounded-2xl border border-border p-6">
            <h3 class="text-sm font-medium text-muted-foreground mb-2">Payment Status</h3>
            <span
              :class="[
                'inline-block px-4 py-2 text-sm font-medium rounded-full',
                getPaymentStatusDisplay(currentOrder.payment_status).color,
              ]"
            >
              {{ getPaymentStatusDisplay(currentOrder.payment_status).text }}
            </span>
            <p v-if="currentOrder.paid_at" class="mt-2 text-xs text-muted-foreground">
              Paid on {{ formatDate(currentOrder.paid_at) }}
            </p>
          </div>

          <div class="bg-card rounded-2xl border border-border p-6">
            <h3 class="text-sm font-medium text-muted-foreground mb-2">Fulfillment Status</h3>
            <span
              :class="[
                'inline-block px-4 py-2 text-sm font-medium rounded-full',
                getFulfillmentStatusDisplay(currentOrder.fulfillment_status).color,
              ]"
            >
              {{ getFulfillmentStatusDisplay(currentOrder.fulfillment_status).text }}
            </span>
          </div>
        </div>

        <!-- Order Items -->
        <div class="bg-card rounded-4xl border border-border p-6">
          <h2 class="text-lg font-semibold text-foreground mb-4">Order Items</h2>
          <div class="space-y-4">
            <div
              v-for="item in currentOrder.items"
              :key="item.id"
              class="flex items-start gap-4 pb-4 border-b border-border last:border-b-0 last:pb-0"
            >
              <div class="flex-1">
                <h3 class="font-medium text-foreground">{{ item.product_name }}</h3>
                <p class="text-sm text-muted-foreground">{{ item.price_display }} each</p>
                <p class="text-sm text-muted-foreground">Quantity: {{ item.quantity }}</p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-foreground">{{ item.subtotal_display }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="bg-card rounded-4xl border border-border p-6">
          <h2 class="text-lg font-semibold text-foreground mb-4">Order Summary</h2>
          <div class="space-y-3">
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Subtotal</span>
              <span class="text-foreground">{{ currentOrder.subtotal_display }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Shipping</span>
              <span class="text-foreground">${(currentOrder.shipping_cents / 100).toFixed(2)}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-muted-foreground">Tax</span>
              <span class="text-foreground">${(currentOrder.tax_cents / 100).toFixed(2)}</span>
            </div>
            <div class="border-t border-border pt-3 flex justify-between">
              <span class="font-semibold text-foreground">Total</span>
              <span class="font-bold text-primary text-lg">{{ currentOrder.total_display }}</span>
            </div>
          </div>
        </div>

        <!-- Customer Info (if available) -->
        <div
          v-if="currentOrder.customer_email || currentOrder.customer_name"
          class="bg-card rounded-2xl border border-border p-6"
        >
          <h2 class="text-lg font-semibold text-foreground mb-4">Customer Information</h2>
          <div class="space-y-2 text-sm">
            <div v-if="currentOrder.customer_name">
              <span class="text-muted-foreground">Name:</span>
              <span class="text-foreground ml-2">{{ currentOrder.customer_name }}</span>
            </div>
            <div v-if="currentOrder.customer_email">
              <span class="text-muted-foreground">Email:</span>
              <span class="text-foreground ml-2">{{ currentOrder.customer_email }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const {
  currentOrder,
  loading,
  error,
  fetchOrder,
  getPaymentStatusDisplay,
  getFulfillmentStatusDisplay,
} = useOrders()

// Fetch order on mount
onMounted(async () => {
  const orderId = route.params.id as string
  await fetchOrder(orderId)
})

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
