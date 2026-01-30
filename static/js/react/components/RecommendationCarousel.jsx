/**
 * RecommendationCarousel Component
 * 
 * Horizontal scrollable carousel for mobile/tablet views.
 * Shows recommendations in a horizontal scroll container.
 * 
 * Features:
 * - Touch-friendly scrolling
 * - Responsive spacing
 * - Smooth animations
 */

import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import RecommendationCard from './RecommendationCard';

const RecommendationCarousel = ({
  products,
  title,
  onAddToCart,
  onAddToWishlist,
  isLoading,
  error,
}) => {
  const scrollContainerRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const scroll = (direction) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const scrollAmount = 320; // Width of card + gap
    const newScroll =
      container.scrollLeft + (direction === 'left' ? -scrollAmount : scrollAmount);

    container.scrollTo({
      left: newScroll,
      behavior: 'smooth',
    });
  };

  const handleScroll = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    setShowLeftArrow(container.scrollLeft > 0);
    setShowRightArrow(
      container.scrollLeft < container.scrollWidth - container.clientWidth - 10
    );
  };

  return (
    <motion.section
      className="recommendation-carousel-section py-5"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Section Header */}
      <div className="container-fluid px-4 mb-4">
        <h3 className="fw-bold mb-1">{title}</h3>
        <p className="text-muted small">Scroll to see more</p>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="container-fluid px-4">
          <div className="d-flex gap-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="skeleton-card" style={{ width: '280px' }}>
                <div
                  className="skeleton"
                  style={{ height: '250px', marginBottom: '10px' }}
                />
                <div className="skeleton" style={{ height: '20px', width: '80%' }} />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="alert alert-warning mx-4" role="alert">
          {error}
        </div>
      )}

      {/* Carousel Container */}
      {!isLoading && !error && products.length > 0 && (
        <div className="position-relative">
          {/* Left Arrow */}
          {showLeftArrow && (
            <motion.button
              className="carousel-arrow carousel-arrow-left"
              onClick={() => scroll('left')}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              ❮
            </motion.button>
          )}

          {/* Products Container */}
          <div
            ref={scrollContainerRef}
            className="products-scroll-container"
            onScroll={handleScroll}
            style={{
              overflowX: 'auto',
              scrollBehavior: 'smooth',
              paddingLeft: '1rem',
              paddingRight: '1rem',
              gap: '1rem',
              display: 'flex',
              scrollSnapType: 'x mandatory',
            }}
          >
            {products.map((product, index) => (
              <div
                key={product.pid}
                style={{
                  flexShrink: 0,
                  width: '280px',
                  scrollSnapAlign: 'start',
                }}
              >
                <RecommendationCard
                  product={product}
                  index={index}
                  onAddToCart={onAddToCart}
                  onAddToWishlist={onAddToWishlist}
                />
              </div>
            ))}
          </div>

          {/* Right Arrow */}
          {showRightArrow && (
            <motion.button
              className="carousel-arrow carousel-arrow-right"
              onClick={() => scroll('right')}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              ❯
            </motion.button>
          )}
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && products.length === 0 && (
        <div className="text-center text-muted py-5">
          <p>No recommendations available at this time.</p>
        </div>
      )}
    </motion.section>
  );
};

export default RecommendationCarousel;