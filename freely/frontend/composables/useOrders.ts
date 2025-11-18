/**
 * Orders composable for Freely
 * Manages order history and details
 */

export interface OrderItem {
  id: string
  product_id: string | null
  product_name: string
  product_slug: string
  quantity: number
  price_cents: number
  currency: string
  price_display: string
  subtotal_cents: number
  subtotal_display: string
}

export interface Order {
  id: string
  order_number: string
  user_id: string | null
  organization_id: string
  customer_email: string | null
  customer_name: string | null
  items: OrderItem[]
  subtotal_cents: number
  tax_cents: number
  shipping_cents: number
  total_cents: number
  currency: string
  total_display: string
  subtotal_display: string
  payment_status: string
  fulfillment_status: string
  created_at: string
  paid_at: string | null
}

export interface OrderListResponse {
  orders: Order[]
  total: number
  page: number
  page_size: number
}

export const useOrders = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const orders = useState<Order[]>('orders:list', () => [])
  const currentOrder = useState<Order | null>('orders:current', () => null)
  const loading = useState<boolean>('orders:loading', () => false)
  const error = useState<string | null>('orders:error', () => null)
  const total = useState<number>('orders:total', () => 0)
  const page = useState<number>('orders:page', () => 1)
  const pageSize = useState<number>('orders:page_size', () => 20)

  /**
   * Fetch user's orders with pagination
   */
  const fetchOrders = async (params?: { page?: number; pageSize?: number }): Promise<void> => {
    loading.value = true
    error.value = null

    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.pageSize) queryParams.append('page_size', params.pageSize.toString())

    try {
      const response = await $fetch<OrderListResponse>(
        `${apiUrl}/v1/checkout/orders?${queryParams.toString()}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      )

      orders.value = response.orders
      total.value = response.total
      page.value = response.page
      pageSize.value = response.page_size
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch orders'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch a single order by ID
   */
  const fetchOrder = async (orderId: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Order>(`${apiUrl}/v1/checkout/orders/${orderId}`, {
        method: 'GET',
        credentials: 'include',
      })

      currentOrder.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch order'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch order by order number (public endpoint)
   */
  const fetchOrderByNumber = async (orderNumber: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Order>(
        `${apiUrl}/v1/checkout/orders/number/${orderNumber}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      )

      currentOrder.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch order'
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear current order
   */
  const clearCurrentOrder = () => {
    currentOrder.value = null
  }

  /**
   * Clear error state
   */
  const clearError = () => {
    error.value = null
  }

  /**
   * Get payment status display
   */
  const getPaymentStatusDisplay = (status: string): { text: string; color: string } => {
    const statusMap: Record<string, { text: string; color: string }> = {
      pending: { text: 'Pending', color: 'text-yellow-600 bg-yellow-50' },
      paid: { text: 'Paid', color: 'text-green-600 bg-green-50' },
      failed: { text: 'Failed', color: 'text-red-600 bg-red-50' },
      refunded: { text: 'Refunded', color: 'text-gray-600 bg-gray-50' },
    }
    return statusMap[status] || { text: status, color: 'text-gray-600 bg-gray-50' }
  }

  /**
   * Get fulfillment status display
   */
  const getFulfillmentStatusDisplay = (
    status: string
  ): { text: string; color: string } => {
    const statusMap: Record<string, { text: string; color: string }> = {
      unfulfilled: { text: 'Unfulfilled', color: 'text-gray-600 bg-gray-50' },
      fulfilled: { text: 'Fulfilled', color: 'text-blue-600 bg-blue-50' },
      shipped: { text: 'Shipped', color: 'text-purple-600 bg-purple-50' },
      delivered: { text: 'Delivered', color: 'text-green-600 bg-green-50' },
    }
    return statusMap[status] || { text: status, color: 'text-gray-600 bg-gray-50' }
  }

  return {
    // State
    orders: readonly(orders),
    currentOrder: readonly(currentOrder),
    loading: readonly(loading),
    error: readonly(error),
    total: readonly(total),
    page: readonly(page),
    pageSize: readonly(pageSize),

    // Methods
    fetchOrders,
    fetchOrder,
    fetchOrderByNumber,
    clearCurrentOrder,
    clearError,

    // Helpers
    getPaymentStatusDisplay,
    getFulfillmentStatusDisplay,
  }
}
