import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const OrderConfirmation = ({ orderId }) => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchOrder();
  }, [orderId]);

  const fetchOrder = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/v1/orders/${orderId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch order');

      const data = await response.json();
      setOrder(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="spinner-border" role="status" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container py-5">
        <div className="alert alert-danger">{error}</div>
      </div>
    );
  }

  return (
    <motion.div
      className="container py-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Success Message */}
      <motion.div
        className="card border-0 shadow-sm mb-4 bg-success bg-opacity-10"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <div className="card-body text-center py-5">
          <motion.div
            className="mb-3"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
          >
            <div className="display-1">✓</div>
          </motion.div>
          <h2 className="mb-2">Order Confirmed!</h2>
          <p className="text-muted mb-0">
            Order ID: <strong>{order.order_id}</strong>
          </p>
        </div>
      </motion.div>

      <div className="row">
        {/* Order Details */}
        <div className="col-lg-8">
          {/* Order Items */}
          <motion.div
            className="card shadow-sm mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="card-header bg-light">
              <h5 className="mb-0">Order Items</h5>
            </div>
            <div className="card-body">
              {order.items.map((item) => (
                <div key={item.id} className="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                  <div>
                    <h6 className="mb-1">{item.product_name}</h6>
                    <small className="text-muted">
                      {item.size && `Size: ${item.size}`}
                      {item.color && ` • Color: ${item.color}`}
                    </small>
                  </div>
                  <div className="text-end">
                    <div className="fw-bold">৳{parseFloat(item.product_price).toFixed(2)}</div>
                    <small className="text-muted">x{item.quantity}</small>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Shipping Address */}
          <motion.div
            className="card shadow-sm mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <div className="card-header bg-light">
              <h5 className="mb-0">Shipping Address</h5>
            </div>
            <div className="card-body">
              <p className="mb-1">
                <strong>{order.shipping_address.full_name}</strong>
              </p>
              <p className="mb-1">{order.shipping_address.street_address}</p>
              <p className="mb-1">
                {order.shipping_address.city}, {order.shipping_address.state}{' '}
                {order.shipping_address.postal_code}
              </p>
              <p className="mb-0">
                <strong>Phone:</strong> {order.shipping_address.phone_number}
              </p>
            </div>
          </motion.div>

          {/* Order Timeline */}
          <motion.div
            className="card shadow-sm"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="card-header bg-light">
              <h5 className="mb-0">Order Status</h5>
            </div>
            <div className="card-body">
              <div className="timeline">
                {order.status_history.reverse().map((status, index) => (
                  <div key={status.id} className="timeline-item">
                    <div className="timeline-marker">
                      <div className="timeline-dot bg-primary" />
                    </div>
                    <div className="timeline-content">
                      <h6 className="mb-1">{status.status_display}</h6>
                      <small className="text-muted">
                        {new Date(status.status_date).toLocaleString()}
                      </small>
                      {status.notes && (
                        <p className="mb-0 mt-1 small">{status.notes}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Summary Sidebar */}
        <div className="col-lg-4">
          <motion.div
            className="card shadow-sm sticky-top mb-4"
            style={{ top: '20px' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="card-header bg-light">
              <h5 className="mb-0">Order Summary</h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>৳{parseFloat(order.subtotal).toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Discount:</span>
                <span>-৳{parseFloat(order.discount_amount).toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>৳{parseFloat(order.shipping_cost).toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-3">
                <span>Tax:</span>
                <span>৳{parseFloat(order.tax_amount).toFixed(2)}</span>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-3">
                <strong>Total:</strong>
                <strong className="text-primary fs-5">
                  ৳{parseFloat(order.total_price).toFixed(2)}
                </strong>
              </div>

              <div className="alert alert-info mb-3">
                <small>
                  <strong>Payment Method:</strong> {order.payment_method_display}
                </small>
              </div>

              <motion.button
                className="btn btn-primary w-100 mb-2"
                onClick={() => window.print()}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                🖨️ Print Order
              </motion.button>

              <a href="/my-orders" className="btn btn-outline-primary w-100 mb-2">
                View All Orders
              </a>

              <a href="/shop" className="btn btn-outline-secondary w-100">
                Continue Shopping
              </a>
            </div>
          </motion.div>

          {/* Next Steps */}
          <motion.div
            className="card shadow-sm border-info"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="card-header bg-light border-info">
              <h5 className="mb-0">What's Next?</h5>
            </div>
            <div className="card-body">
              <ol className="mb-0 small">
                <li>Check your email for order confirmation</li>
                <li>We'll prepare your order for shipping</li>
                <li>Track your shipment in real-time</li>
                <li>Receive your order at your doorstep</li>
              </ol>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default OrderConfirmation;