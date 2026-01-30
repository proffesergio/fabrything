/**
 * RecommendationCard Component
 * 
 * Displays a single product recommendation card with:
 * - Product image
 * - Title
 * - Price (current + original)
 * - Discount badge
 * - Rating stars
 * - Quick action buttons (Add to Cart, Wishlist)
 * 
 * Uses Framer Motion for entrance animations
 */

import React from 'react';
import { motion } from 'framer-motion';

const RecommendationCard = ({ product, index, onAddToCart, onAddToWishlist }) => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [addedToWishlist, setAddedToWishlist] = React.useState(false);

  // Framer Motion animation variants
  const cardVariants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.95,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        delay: index * 0.1, // Stagger cards
        ease: "easeOut",
      },
    },
    hover: {
      y: -8,
      boxShadow: "0 12px 24px rgba(0, 0, 0, 0.15)",
      transition: {
        duration: 0.3,
      },
    },
  };

  const imageVariants = {
    hover: {
      scale: 1.05,
      transition: {
        duration: 0.3,
      },
    },
  };

  const handleAddToCart = async () => {
    setIsLoading(true);
    try {
      await onAddToCart(product.pid);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddToWishlist = async () => {
    try {
      await onAddToWishlist(product.pid);
      setAddedToWishlist(!addedToWishlist);
    } catch (error) {
      console.error('Error adding to wishlist:', error);
    }
  };

  return (
    <motion.div
      className="recommendation-card card h-100 border-0 shadow-sm"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover="hover"
    >
      {/* Product Image */}
      <motion.div
        className="position-relative overflow-hidden"
        style={{ height: '250px' }}
      >
        <motion.img
          src={product.image}
          alt={product.title}
          className="card-img-top w-100 h-100 object-fit-cover"
          variants={imageVariants}
          loading="lazy"
        />

        {/* Discount Badge */}
        {product.discount_percent > 0 && (
          <motion.div
            className="position-absolute top-0 end-0 badge bg-danger m-2"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
          >
            -{product.discount_percent}%
          </motion.div>
        )}

        {/* Stock Badge */}
        {!product.in_stock && (
          <div className="position-absolute inset-0 bg-dark bg-opacity-50 d-flex align-items-center justify-content-center">
            <span className="text-white fw-bold">Out of Stock</span>
          </div>
        )}
      </motion.div>

      {/* Card Body */}
      <div className="card-body d-flex flex-column">
        {/* Category */}
        <small className="text-muted mb-1">{product.category_title}</small>

        {/* Title */}
        <h6 className="card-title text-truncate mb-2" title={product.title}>
          {product.title}
        </h6>

        {/* Rating */}
        <div className="mb-2">
          <div className="d-flex align-items-center gap-1">
            <div className="text-warning">
              {'★'.repeat(Math.round(product.average_rating))}
              {'☆'.repeat(5 - Math.round(product.average_rating))}
            </div>
            <small className="text-muted">
              ({product.review_count})
            </small>
          </div>
        </div>

        {/* Price */}
        <div className="mb-3">
          <div className="h5 text-primary mb-0">${product.price}</div>
          {product.old_price > product.price && (
            <small className="text-muted text-decoration-line-through">
              ${product.old_price}
            </small>
          )}
        </div>

        {/* Action Buttons */}
        <div className="d-flex gap-2 mt-auto">
          <motion.button
            className="btn btn-sm btn-primary flex-grow-1"
            onClick={handleAddToCart}
            disabled={isLoading || !product.in_stock}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                />
                Adding...
              </>
            ) : (
              'Add to Cart'
            )}
          </motion.button>

          <motion.button
            className={`btn btn-sm ${
              addedToWishlist ? 'btn-danger' : 'btn-outline-secondary'
            }`}
            onClick={handleAddToWishlist}
            title={addedToWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            {addedToWishlist ? '❤️' : '🤍'}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

export default RecommendationCard;