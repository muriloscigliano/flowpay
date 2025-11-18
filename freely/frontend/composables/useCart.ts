/**
 * Cart and Checkout composable for Freely
 * Manages shopping cart and checkout state
 */

export interface CartItem {
  id: string
  product_id: string | null
  product_name: string
  product_slug: string
  product_image_url: string | null
  quantity: number
  price_cents: number
  currency: string
  price_display: string
  subtotal_cents: number
  subtotal_display: string
  created_at: string
}

export interface Cart {
  id: string
  items: CartItem[]
  total_cents: number
  total_display: string
  item_count: number
  created_at: string
}

export interface AddToCartRequest {
  product_id: string
  quantity?: number
}

export interface UpdateCartItemRequest {
  quantity: number
}

export interface CheckoutRequest {
  customer_email?: string
  customer_name?: string
  shipping_address?: {
    line1: string
    line2?: string
    city: string
    state: string
    postal_code: string
    country?: string
  }
  customer_notes?: string
}

export interface CheckoutResponse {
  order_id: string
  order_number: string
  client_secret: string
  total_cents: number
  total_display: string
}

export const useCart = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const cart = useState<Cart | null>('cart:data', () => null)
  const loading = useState<boolean>('cart:loading', () => false)
  const error = useState<string | null>('cart:error', () => null)

  /**
   * Fetch current cart
   */
  const fetchCart = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Cart>(`${apiUrl}/v1/cart`, {
        method: 'GET',
        credentials: 'include',
      })

      cart.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch cart'
      // Initialize empty cart on error
      cart.value = {
        id: '',
        items: [],
        total_cents: 0,
        total_display: '$0.00',
        item_count: 0,
        created_at: new Date().toISOString(),
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Add product to cart
   */
  const addToCart = async (productId: string, quantity: number = 1): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Cart>(`${apiUrl}/v1/cart/items`, {
        method: 'POST',
        body: {
          product_id: productId,
          quantity,
        },
        credentials: 'include',
      })

      cart.value = response
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to add to cart'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Update cart item quantity
   */
  const updateCartItem = async (itemId: string, quantity: number): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Cart>(`${apiUrl}/v1/cart/items/${itemId}`, {
        method: 'PATCH',
        body: { quantity },
        credentials: 'include',
      })

      cart.value = response
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to update cart item'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Remove item from cart
   */
  const removeFromCart = async (itemId: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(`${apiUrl}/v1/cart/items/${itemId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      // Refetch cart
      await fetchCart()
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to remove from cart'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear entire cart
   */
  const clearCart = async (): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(`${apiUrl}/v1/cart`, {
        method: 'DELETE',
        credentials: 'include',
      })

      cart.value = {
        id: '',
        items: [],
        total_cents: 0,
        total_display: '$0.00',
        item_count: 0,
        created_at: new Date().toISOString(),
      }
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to clear cart'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Create checkout and get Stripe client secret
   */
  const createCheckout = async (data: CheckoutRequest): Promise<CheckoutResponse | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<CheckoutResponse>(`${apiUrl}/v1/checkout`, {
        method: 'POST',
        body: data,
        credentials: 'include',
      })

      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to create checkout'
      return null
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
    // State
    cart: readonly(cart),
    loading: readonly(loading),
    error: readonly(error),
    itemCount: computed(() => cart.value?.item_count || 0),
    total: computed(() => cart.value?.total_display || '$0.00'),

    // Cart methods
    fetchCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,

    // Checkout methods
    createCheckout,

    // Utility methods
    clearError,
  }
}
