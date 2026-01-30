/**
 * useRecommendations Hook
 * 
 * Custom React hook for fetching and managing recommendations.
 * Handles:
 * - API calls with JWT authentication
 * - Loading/error states
 * - Token refresh on 401
 * - Caching of results
 * 
 * Usage:
 *   const { products, loading, error } = useRecommendations('personalized');
 */

import { useState, useEffect } from 'react';

const useRecommendations = (type = 'trending', options = {}) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cached, setCached] = useState(false);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get JWT token from localStorage
        const token = localStorage.getItem('access_token');

        // Determine API endpoint based on type
        let endpoint = `/api/v1/recommendations/${type}/`;
        if (options.productId) {
          endpoint = `/api/v1/products/${options.productId}/similar/`;
        }

        // Add query parameters
        const params = new URLSearchParams();
        if (options.limit) params.append('limit', options.limit);
        if (options.category) params.append('category', options.category);

        const url = endpoint + (params.toString() ? `?${params.toString()}` : '');

        // Prepare headers
        const headers = {
          'Content-Type': 'application/json',
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        // Fetch recommendations
        const response = await fetch(url, {
          method: 'GET',
          headers,
        });

        // Handle 401 - Token expired, try to refresh
        if (response.status === 401 && token) {
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            try {
              const refreshResponse = await fetch('/api/v1/auth/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken }),
              });

              if (refreshResponse.ok) {
                const { access } = await refreshResponse.json();
                localStorage.setItem('access_token', access);

                // Retry original request with new token
                headers['Authorization'] = `Bearer ${access}`;
                const retryResponse = await fetch(url, {
                  method: 'GET',
                  headers,
                });

                if (!retryResponse.ok) {
                  throw new Error(`HTTP ${retryResponse.status}`);
                }

                const data = await retryResponse.json();
                setProducts(data.products || []);
                setCached(data.cached || false);
              }
            } catch (refreshError) {
              console.error('Token refresh failed:', refreshError);
              setError('Authentication failed. Please log in again.');
            }
          }
        } else if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        } else {
          const data = await response.json();
          setProducts(data.products || []);
          setCached(data.cached || false);
        }
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError(err.message || 'Failed to load recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [type, options.productId, options.limit, options.category]);

  return { products, loading, error, cached };
};

export default useRecommendations;