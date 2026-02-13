/**
 * useCart Hook
 * 
 * Custom hook for cart operations (add/remove items, get cart).
 * Handles:
 * - Adding items to cart
 * - Removing items
 * - Updating quantities
 * - Error handling
 * - Optimistic updates
 */

import { useState, useCallback, useEffect } from 'react';
/**
const useCart = () => {
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const getToken = () => localStorage.getItem('access_token');

  const addToCart = async (productId, quantity = 1) => {
    try {
      setError(null);
      setSuccess(null);

      const token = getToken();
      if (!token) {
        setError('Please log in to add items to cart');
        throw new Error('Not authenticated');
      }

      const response = await fetch('/api/v1/cart/add_item/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: quantity,
        }),
      });

      if (response.status === 401) {
        // Token expired - redirect to login
        localStorage.clear();
        window.location.href = '/user/login/';
        throw new Error('Session expired');
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setSuccess('Item added to cart!');
      return data;
    } catch (err) {
      console.error('Error adding to cart:', err);
      setError(err.message || 'Failed to add item to cart');
      throw err;
    }
  };

  const removeFromCart = async (productTitle) => {
    try {
      setError(null);

      const token = getToken();
      if (!token) throw new Error('Not authenticated');

      const response = await fetch('/api/v1/cart/remove_item/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          item: productTitle,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error removing from cart:', err);
      setError(err.message || 'Failed to remove item');
      throw err;
    }
  };

  const addToWishlist = async (productId) => {
    try {
      setError(null);

      const token = getToken();
      if (!token) {
        setError('Please log in to save items');
        throw new Error('Not authenticated');
      }

      const response = await fetch('/api/v1/wishlist/add/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          product_id: productId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error adding to wishlist:', err);
      setError(err.message || 'Failed to save item');
      throw err;
    }
  };

  return {
    addToCart,
    removeFromCart,
    addToWishlist,
    error,
    success,
  };
};
*/

/**
 * Custom hook for shopping cart operations
 * Manages cart state and API calls
 */
export const useCart = (onError = null) => {
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_BASE = '/api/v1';

    // Fetch current cart
    const fetchCart = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/cart/current_cart/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Failed to fetch cart');
            const data = await response.json();
            setCart(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
        }
    }, [onError]);

    // Add item to cart
    const addItem = useCallback(async (productId, quantity = 1, size = '', color = '') => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/cart/add_item/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity,
                    size,
                    color
                })
            });
            if (!response.ok) throw new Error('Failed to add item');
            const data = await response.json();
            setCart(data);
            setError(null);
            return data;
        } catch (err) {
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
        }
    }, [onError]);

    // Remove item from cart
    const removeItem = useCallback(async (itemId) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/cart/remove_item/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ item_id: itemId })
            });
            if (!response.ok) throw new Error('Failed to remove item');
            const data = await response.json();
            setCart(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
        }
    }, [onError]);

    // Update item quantity
    const updateItem = useCallback(async (itemId, quantity) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/cart/update_item/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quantity
                })
            });
            if (!response.ok) throw new Error('Failed to update item');
            const data = await response.json();
            setCart(data);
            setError(null);
        } catch (err) {
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
        }
    }, [onError]);

    // Clear cart
    const clearCart = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/cart/clear/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Failed to clear cart');
            setCart({ items: [], price: 0 });
            setError(null);
        } catch (err) {
            setError(err.message);
            if (onError) onError(err);
        } finally {
            setLoading(false);
        }
    }, [onError]);

    return {
        cart,
        loading,
        error,
        fetchCart,
        addItem,
        removeItem,
        updateItem,
        clearCart
    };
};
export default useCart;