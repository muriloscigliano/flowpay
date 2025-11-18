<template>
  <div class="min-h-screen bg-background">
    <!-- Header -->
    <header class="sticky top-0 z-10 bg-card border-b border-border">
      <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-foreground">Shopping Cart</h1>
          <p class="text-sm text-muted-foreground">{{ itemCount }} item{{ itemCount !== 1 ? 's' : '' }}</p>
        </div>
        <NuxtLink to="/products" class="text-sm text-primary hover:text-primary/80">
          Continue Shopping
        </NuxtLink>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-6xl mx-auto px-4 py-8">
      <div v-if="loading && !cart" class="text-center py-12">
        <div class="inline-block w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        <p class="mt-4 text-muted-foreground">Loading cart...</p>
      </div>

      <!-- Empty Cart -->
      <div v-else-if="!cart || cart.items.length === 0" class="text-center py-12 bg-card rounded-4xl border border-border">
        <div class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-foreground mb-2">Your cart is empty</h3>
        <p class="text-muted-foreground mb-6">Add some products to get started</p>
        <NuxtLink to="/products" class="inline-block px-6 py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90">
          Browse Products
        </NuxtLink>
      </div>

      <!-- Cart Items -->
      <div v-else class="grid lg:grid-cols-3 gap-8">
        <!-- Items List -->
        <div class="lg:col-span-2 space-y-4">
          <div v-for="item in cart.items" :key="item.id" class="bg-card rounded-2xl border border-border p-4 flex gap-4">
            <!-- Product Image -->
            <div class="w-24 h-24 flex-shrink-0 bg-muted rounded-lg flex items-center justify-center">
              <img v-if="item.product_image_url" :src="item.product_image_url" :alt="item.product_name" class="w-full h-full object-cover rounded-lg" />
              <svg v-else class="w-10 h-10 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
              </svg>
            </div>

            <!-- Product Info -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-foreground truncate">{{ item.product_name }}</h3>
              <p class="text-sm text-muted-foreground">{{ item.price_display }} each</p>

              <!-- Quantity Controls -->
              <div class="mt-3 flex items-center gap-3">
                <div class="flex items-center border border-input rounded-lg">
                  <button @click="decrementQuantity(item)" class="px-3 py-1 hover:bg-muted">-</button>
                  <span class="px-4 py-1 border-x border-input">{{ item.quantity }}</span>
                  <button @click="incrementQuantity(item)" class="px-3 py-1 hover:bg-muted">+</button>
                </div>
                <button @click="removeItem(item)" class="text-sm text-destructive hover:text-destructive/80">
                  Remove
                </button>
              </div>
            </div>

            <!-- Subtotal -->
            <div class="text-right">
              <p class="font-semibold text-foreground">{{ item.subtotal_display }}</p>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="lg:col-span-1">
          <div class="bg-card rounded-4xl border border-border p-6 sticky top-24">
            <h2 class="text-lg font-semibold text-foreground mb-4">Order Summary</h2>

            <div class="space-y-3 mb-6">
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Subtotal</span>
                <span class="text-foreground">{{ cart.total_display }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Shipping</span>
                <span class="text-foreground">$0.00</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-muted-foreground">Tax</span>
                <span class="text-foreground">$0.00</span>
              </div>
              <div class="border-t border-border pt-3 flex justify-between">
                <span class="font-semibold text-foreground">Total</span>
                <span class="font-bold text-primary text-lg">{{ cart.total_display }}</span>
              </div>
            </div>

            <button @click="handleCheckout" :disabled="loading" class="w-full py-3 bg-primary text-primary-foreground font-medium rounded-lg hover:bg-primary/90 disabled:opacity-50">
              Proceed to Checkout
            </button>

            <button @click="handleClearCart" class="w-full mt-3 py-2 text-sm text-destructive hover:text-destructive/80">
              Clear Cart
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const { cart, itemCount, loading, fetchCart, updateCartItem, removeFromCart, clearCart } = useCart()
const router = useRouter()

// Fetch cart on mount
onMounted(async () => {
  await fetchCart()
})

const incrementQuantity = async (item: any) => {
  await updateCartItem(item.id, item.quantity + 1)
}

const decrementQuantity = async (item: any) => {
  if (item.quantity > 1) {
    await updateCartItem(item.id, item.quantity - 1)
  }
}

const removeItem = async (item: any) => {
  if (confirm(`Remove ${item.product_name} from cart?`)) {
    await removeFromCart(item.id)
  }
}

const handleClearCart = async () => {
  if (confirm('Clear all items from cart?')) {
    await clearCart()
  }
}

const handleCheckout = () => {
  // For Week 3, this would redirect to a Stripe checkout page
  // For now, show alert
  alert('Checkout functionality coming soon! (Stripe integration in progress)')
}

definePageMeta({
  layout: false,
  middleware: 'auth',
})
</script>
