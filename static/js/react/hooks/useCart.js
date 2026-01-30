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

import { useState } from 'react';

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

export default useCart;