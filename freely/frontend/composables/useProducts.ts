/**
 * Products and Categories composable for Freely
 * Manages product catalog state and operations
 */

export interface Category {
  id: string
  name: string
  slug: string
  description: string | null
  organization_id: string
  created_at: string
}

export interface Product {
  id: string
  name: string
  slug: string
  description: string | null
  price_cents: number
  currency: string
  price_display: string
  image_urls: string[]
  stock_available: number | null
  is_available: boolean
  is_digital: boolean
  organization_id: string
  created_at: string
  categories: Category[]
  category_ids: string[]
}

export interface ProductListResponse {
  products: Product[]
  total: number
  page: number
  page_size: number
}

export interface ProductCreate {
  name: string
  slug: string
  description?: string
  price_cents: number
  currency?: string
  image_urls?: string[]
  stock_available?: number
  is_available?: boolean
  is_digital?: boolean
  category_ids?: string[]
}

export interface ProductUpdate {
  name?: string
  slug?: string
  description?: string
  price_cents?: number
  currency?: string
  image_urls?: string[]
  stock_available?: number
  is_available?: boolean
  is_digital?: boolean
  category_ids?: string[]
}

export interface CategoryCreate {
  name: string
  slug: string
  description?: string
}

export interface CategoryUpdate {
  name?: string
  slug?: string
  description?: string
}

export const useProducts = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiUrl

  const products = useState<Product[]>('products:list', () => [])
  const currentProduct = useState<Product | null>('products:current', () => null)
  const categories = useState<Category[]>('products:categories', () => [])
  const loading = useState<boolean>('products:loading', () => false)
  const error = useState<string | null>('products:error', () => null)
  const total = useState<number>('products:total', () => 0)
  const page = useState<number>('products:page', () => 1)
  const pageSize = useState<number>('products:page_size', () => 20)

  /**
   * Fetch all categories
   */
  const fetchCategories = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Category[]>(`${apiUrl}/v1/products/categories`, {
        method: 'GET',
        credentials: 'include',
      })

      categories.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch categories'
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new category
   */
  const createCategory = async (data: CategoryCreate): Promise<Category | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Category>(`${apiUrl}/v1/products/categories`, {
        method: 'POST',
        body: data,
        credentials: 'include',
      })

      categories.value.push(response)
      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to create category'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a category
   */
  const updateCategory = async (
    categoryId: string,
    data: CategoryUpdate
  ): Promise<Category | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Category>(
        `${apiUrl}/v1/products/categories/${categoryId}`,
        {
          method: 'PATCH',
          body: data,
          credentials: 'include',
        }
      )

      // Update in categories list
      const index = categories.value.findIndex((c) => c.id === categoryId)
      if (index !== -1) {
        categories.value[index] = response
      }

      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to update category'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a category
   */
  const deleteCategory = async (categoryId: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(`${apiUrl}/v1/products/categories/${categoryId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      // Remove from categories list
      categories.value = categories.value.filter((c) => c.id !== categoryId)
      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to delete category'
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch products with filtering and pagination
   */
  const fetchProducts = async (params?: {
    categoryId?: string
    search?: string
    isAvailable?: boolean
    page?: number
    pageSize?: number
  }): Promise<void> => {
    loading.value = true
    error.value = null

    const queryParams = new URLSearchParams()
    if (params?.categoryId) queryParams.append('category_id', params.categoryId)
    if (params?.search) queryParams.append('search', params.search)
    if (params?.isAvailable !== undefined)
      queryParams.append('is_available', params.isAvailable.toString())
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.pageSize) queryParams.append('page_size', params.pageSize.toString())

    try {
      const response = await $fetch<ProductListResponse>(
        `${apiUrl}/v1/products?${queryParams.toString()}`,
        {
          method: 'GET',
          credentials: 'include',
        }
      )

      products.value = response.products
      total.value = response.total
      page.value = response.page
      pageSize.value = response.page_size
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch products'
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch a single product by ID
   */
  const fetchProduct = async (productId: string): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Product>(`${apiUrl}/v1/products/${productId}`, {
        method: 'GET',
        credentials: 'include',
      })

      currentProduct.value = response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to fetch product'
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new product
   */
  const createProduct = async (data: ProductCreate): Promise<Product | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Product>(`${apiUrl}/v1/products`, {
        method: 'POST',
        body: data,
        credentials: 'include',
      })

      products.value.unshift(response)
      total.value += 1
      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to create product'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a product
   */
  const updateProduct = async (
    productId: string,
    data: ProductUpdate
  ): Promise<Product | null> => {
    loading.value = true
    error.value = null

    try {
      const response = await $fetch<Product>(`${apiUrl}/v1/products/${productId}`, {
        method: 'PATCH',
        body: data,
        credentials: 'include',
      })

      // Update in products list
      const index = products.value.findIndex((p) => p.id === productId)
      if (index !== -1) {
        products.value[index] = response
      }

      // Update current product if it's the same
      if (currentProduct.value?.id === productId) {
        currentProduct.value = response
      }

      return response
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to update product'
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Delete a product
   */
  const deleteProduct = async (productId: string): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      await $fetch(`${apiUrl}/v1/products/${productId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      // Remove from products list
      products.value = products.value.filter((p) => p.id !== productId)
      total.value -= 1

      // Clear current product if it's the same
      if (currentProduct.value?.id === productId) {
        currentProduct.value = null
      }

      return true
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to delete product'
      return false
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

  /**
   * Clear current product
   */
  const clearCurrentProduct = () => {
    currentProduct.value = null
  }

  return {
    // State
    products: readonly(products),
    currentProduct: readonly(currentProduct),
    categories: readonly(categories),
    loading: readonly(loading),
    error: readonly(error),
    total: readonly(total),
    page: readonly(page),
    pageSize: readonly(pageSize),

    // Category methods
    fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory,

    // Product methods
    fetchProducts,
    fetchProduct,
    createProduct,
    updateProduct,
    deleteProduct,

    // Utility methods
    clearError,
    clearCurrentProduct,
  }
}
