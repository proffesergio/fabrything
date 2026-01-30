/**
 * React App Component
 * 
 * Main React application for recommendation features.
 * Can be mounted on multiple pages:
 * - Homepage (trending + personalized)
 * - Product detail page (similar products)
 * - Category page (popular in category)
 * 
 * Usage:
 *   In Django template: {% include 'react_recommendations.html' %}
 *   Then initialize with: window.initRecommendations()
 */

import React, { useState, useEffect } from 'react';
import { useMediaQuery } from './hooks/useMediaQuery';
import useRecommendations from './hooks/useRecommendations';
import useCart from './hooks/useCart';
import RecommendationCarousel from './components/RecommendationCarousel';
import RecommendationGrid from './components/RecommendationGrid';

const RecommendationApp = ({ initialType = 'trending', sectionTitle = 'Recommended for You' }) => {
  const isMobile = useMediaQuery('(max-width: 768px)');
  const { products, loading, error } = useRecommendations(initialType);
  const { addToCart, addToWishlist, error: cartError } = useCart();

  const handleAddToCart = async (productId) => {
    try {
      await addToCart(productId, 1);
      // Show success toast/notification
      alert('Added to cart!');
    } catch (err) {
      alert(err.message || 'Failed to add to cart');
    }
  };

  const handleAddToWishlist = async (productId) => {
    try {
      await addToWishlist(productId);
      // Show success toast/notification
      alert('Added to wishlist!');
    } catch (err) {
      alert(err.message || 'Failed to add to wishlist');
    }
  };

  // Use carousel on mobile, grid on desktop
  const Component = isMobile ? RecommendationCarousel : RecommendationGrid;

  return (
    <Component
      products={products}
      title={sectionTitle}
      onAddToCart={handleAddToCart}
      onAddToWishlist={handleAddToWishlist}
      isLoading={loading}
      error={error || cartError}
    />
  );
};

export default RecommendationApp;