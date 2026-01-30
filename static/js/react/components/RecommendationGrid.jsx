/**
 * RecommendationGrid Component
 * 
 * Grid layout for desktop/larger screens.
 * Shows recommendations in a responsive Bootstrap grid.
 * 
 * Features:
 * - Responsive columns (4 on desktop, 2 on tablet, 1 on mobile)
 * - Staggered entrance animations
 * - Optimized for larger screens
 */

import React from 'react';
import { motion } from 'framer-motion';
import RecommendationCard from './RecommendationCard';

const RecommendationGrid = ({
  products,
  title,
  onAddToCart,
  onAddToWishlist,
  isLoading,
  error,
}) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <motion.section
      className="recommendation-grid-section py-5"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container-fluid px-4">
        {/* Section Header */}
        <h3 className="fw-bold mb-4">{title}</h3>

        {/* Loading State */}
        {isLoading && (
          <div className="row g-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="col-lg-3 col-md-6">
                <div className="skeleton-card">
                  <div className="skeleton" style={{ height: '250px' }} />
                  <div className="skeleton mt-2" style={{ height: '20px' }} />
                  <div className="skeleton mt-2" style={{ height: '20px', width: '80%' }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="alert alert-warning" role="alert">
            {error}
          </div>
        )}

        {/* Products Grid */}
        {!isLoading && !error && products.length > 0 && (
          <motion.div
            className="row g-3"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            {products.map((product, index) => (
              <div key={product.pid} className="col-lg-3 col-md-6 col-sm-12">
                <RecommendationCard
                  product={product}
                  index={index}
                  onAddToCart={onAddToCart}
                  onAddToWishlist={onAddToWishlist}
                />
              </div>
            ))}
          </motion.div>
        )}

        {/* Empty State */}
        {!isLoading && !error && products.length === 0 && (
          <div className="text-center text-muted py-5">
            <p>No recommendations available at this time.</p>
          </div>
        )}
      </div>
    </motion.section>
  );
};

export default RecommendationGrid;