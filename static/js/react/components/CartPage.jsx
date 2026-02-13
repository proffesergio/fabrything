import React, { useState } from 'react';
import { motion } from 'framer-motion';
import useCart from '../hooks/useCart';

const CartPage = () => {
  const { cart, loading, error, updateItem, removeItem } = useCart();
  const [showConfirm, setShowConfirm] = useState(null);

  if (loading && !cart) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <motion.div
        className="container py-5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center py-5">
            <h3 className="mb-3">🛒 Your Cart is Empty</h3>
            <p className="text-muted mb-4">
              Add some products to your cart and come back!
            </p>
            <a href="/shop" className="btn btn-primary">
              Continue Shopping
            </a>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="container py-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          {error}
          <button type="button" className="btn-close" data-bs-dismiss="alert" />
        </div>
      )}

      <div className="row">
        {/* Cart Items */}
        <div className="col-lg-8">
          <h2 className="mb-4">Shopping Cart</h2>

          <motion.div
            className="space-y-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {cart.items.map((item) => (
              <motion.div
                key={item.id}
                className="card mb-3 shadow-sm"
                initial={{ x: -50, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: 50, opacity: 0 }}
              >
                <div className="card-body">
                  <div className="row align-items-center">
                    {/* Product Image */}
                    <div className="col-md-2 mb-3 mb-md-0">
                      <img
                        src={item.product_image}
                        alt={item.product_title}
                        className="img-fluid rounded"
                        style={{ maxWidth: '100px', height: 'auto' }}
                      />
                    </div>

                    {/* Product Details */}
                    <div className="col-md-4 mb-3 mb-md-0">
                      <h6 className="mb-2">{item.product_title}</h6>
                      {item.size && (
                        <small className="text-muted">
                          Size: <strong>{item.size}</strong>
                        </small>
                      )}
                      {item.color && (
                        <small className="text-muted ms-2">
                          Color: <strong>{item.color}</strong>
                        </small>
                      )}
                      <div className="mt-2">
                        <span className="badge bg-info">৳{item.product_price}</span>
                      </div>
                    </div>

                    {/* Quantity Controls */}
                    <div className="col-md-3 mb-3 mb-md-0">
                      <div className="input-group">
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() =>
                            updateItem(item.id, Math.max(1, item.quantity - 1))
                          }
                          disabled={loading}
                        >
                          −
                        </button>
                        <input
                          type="number"
                          className="form-control form-control-sm text-center"
                          value={item.quantity}
                          onChange={(e) =>
                            updateItem(item.id, parseInt(e.target.value) || 1)
                          }
                          style={{ width: '60px' }}
                        />
                        <button
                          className="btn btn-sm btn-outline-secondary"
                          onClick={() => updateItem(item.id, item.quantity + 1)}
                          disabled={loading}
                        >
                          +
                        </button>
                      </div>
                    </div>

                    {/* Total & Remove */}
                    <div className="col-md-2 text-md-end">
                      <div className="mb-2">
                        <strong>৳{parseFloat(item.total_price).toFixed(2)}</strong>
                      </div>
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => setShowConfirm(item.id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* Cart Summary */}
        <div className="col-lg-4">
          <motion.div
            className="card shadow-sm sticky-top"
            style={{ top: '20px' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="card-body">
              <h5 className="card-title mb-4">Order Summary</h5>

              <div className="mb-3">
                <div className="d-flex justify-content-between mb-2">
                  <span>Subtotal:</span>
                  <span>৳{parseFloat(cart.subtotal).toFixed(2)}</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Shipping:</span>
                  <span>Calculated at checkout</span>
                </div>
                <div className="d-flex justify-content-between mb-2">
                  <span>Tax:</span>
                  <span>Calculated at checkout</span>
                </div>
                <hr />
                <div className="d-flex justify-content-between">
                  <strong>Total:</strong>
                  <strong className="text-primary fs-5">
                    ৳{parseFloat(cart.subtotal).toFixed(2)}
                  </strong>
                </div>
              </div>

              <div className="mb-3">
                <small className="text-muted">
                  {cart.item_count} item{cart.item_count !== 1 ? 's' : ''} in cart
                </small>
              </div>

              <a href="/checkout" className="btn btn-primary w-100 mb-2">
                Proceed to Checkout
              </a>

              <a href="/shop" className="btn btn-outline-secondary w-100">
                Continue Shopping
              </a>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirm && (
        <motion.div
          className="modal d-block"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="modal-dialog modal-sm">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Remove Item?</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowConfirm(null)}
                />
              </div>
              <div className="modal-body">
                Are you sure you want to remove this item from your cart?
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowConfirm(null)}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={() => {
                    removeItem(showConfirm);
                    setShowConfirm(null);
                  }}
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default CartPage;