import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './CheckoutFlow.css';

const CheckoutFlow = () => {
  // State
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Checkout data
  const [checkoutData, setCheckoutData] = useState({
    cart: null,
    addresses: [],
    shippingMethods: [],
    defaultAddress: null,
  });

  // Form data
  const [formData, setFormData] = useState({
    shipping_address_id: null,
    shipping_method_id: null,
    payment_method: 'cod',
    coupon_code: '',
    notes: '',
  });

  // Calculated totals
  const [totals, setTotals] = useState({
    subtotal: 0,
    discount: 0,
    shipping: 0,
    tax: 0,
    total: 0,
  });

  // Order result
  const [order, setOrder] = useState(null);

  // Lifecycle
  useEffect(() => {
    fetchCheckoutSummary();
  }, []);

  useEffect(() => {
    calculateTotals();
  }, [formData, checkoutData]);

  // API Calls
  const getToken = () => localStorage.getItem('access_token');

  const fetchCheckoutSummary = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const response = await fetch('/api/v1/checkout/summary/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) throw new Error('Failed to fetch checkout data');

      const data = await response.json();
      setCheckoutData(data);

      // Set default address if exists
      if (data.default_address) {
        setFormData(prev => ({
          ...prev,
          shipping_address_id: data.default_address.id,
        }));
      }

      // Set default shipping
      if (data.shipping_methods && data.shipping_methods.length > 0) {
        setFormData(prev => ({
          ...prev,
          shipping_method_id: data.shipping_methods[0].id,
        }));
      }
    } catch (err) {
      setError(err.message);
      console.error('Checkout summary error:', err);
    } finally {
      setLoading(false);
    }
  };

  const validateCheckout = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const response = await fetch('/api/v1/checkout/validate/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Validation failed');
      }

      const data = await response.json();
      if (data.success) {
        setTotals(data.totals);
        return true;
      }
      return false;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const processCheckout = async () => {
    try {
      setLoading(true);
      const token = getToken();
      const response = await fetch('/api/v1/checkout/process/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Checkout failed');
      }

      const data = await response.json();
      if (data.success) {
        setOrder(data.order);
        setSuccess(true);
        return true;
      }
      return false;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Handlers
  const calculateTotals = () => {
    if (!checkoutData.cart) return;

    const subtotal = parseFloat(checkoutData.cart.subtotal || 0);
    const shippingMethod = checkoutData.shippingMethods?.find(
      m => m.id === formData.shipping_method_id
    );
    const shipping = shippingMethod ? parseFloat(shippingMethod.cost) : 0;
    const tax = subtotal * 0.05;
    const discount = 0;
    const total = subtotal - discount + shipping + tax;

    setTotals({
      subtotal: subtotal.toFixed(2),
      discount: discount.toFixed(2),
      shipping: shipping.toFixed(2),
      tax: tax.toFixed(2),
      total: total.toFixed(2),
    });
  };

  const handleNextStep = async () => {
    if (currentStep < 4) {
      const isValid = await validateCheckout();
      if (isValid) {
        setCurrentStep(currentStep + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  };

  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePlaceOrder = async () => {
    const success = await processCheckout();
    if (success) {
      setTimeout(() => {
        window.location.href = `/order-confirmation/${order.order_id}/`;
      }, 1500);
    }
  };

  // Render
  if (loading && !checkoutData.cart) {
    return (
      <div className="checkout-loading">
        <div className="spinner-border"></div>
        <p>Loading checkout data...</p>
      </div>
    );
  }

  if (!checkoutData.cart) {
    return (
      <div className="checkout-error">
        <h3>Oops! Something went wrong</h3>
        <p>{error || 'Could not load checkout data'}</p>
        <a href="/cart" className="btn btn-primary">
          Back to Cart
        </a>
      </div>
    );
  }

  return (
    <div className="checkout-flow">
      {/* Step Indicator */}
      <div className="checkout-steps">
        <div className="container">
          <div className="steps-progress">
            {[1, 2, 3, 4].map((step) => (
              <motion.div
                key={step}
                className={`step ${step <= currentStep ? 'active' : ''} ${step < currentStep ? 'completed' : ''}`}
                onClick={() => step < currentStep && setCurrentStep(step)}
              >
                <div className="step-circle">
                  {step < currentStep ? '✓' : step}
                </div>
                <div className="step-label">
                  {['Address', 'Shipping', 'Payment', 'Review'][step - 1]}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="checkout-content">
        <div className="container">
          <div className="row">
            {/* Left Column - Form */}
            <div className="col-lg-8">
              <motion.div
                className="checkout-form"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
              >
                {/* Step 1: Shipping Address */}
                <AnimatePresence>
                  {currentStep === 1 && (
                    <Step1Address
                      addresses={checkoutData.addresses}
                      selected={formData.shipping_address_id}
                      onSelect={(id) =>
                        setFormData({ ...formData, shipping_address_id: id })
                      }
                    />
                  )}

                  {/* Step 2: Shipping Method */}
                  {currentStep === 2 && (
                    <Step2Shipping
                      methods={checkoutData.shippingMethods}
                      selected={formData.shipping_method_id}
                      onSelect={(id) =>
                        setFormData({ ...formData, shipping_method_id: id })
                      }
                    />
                  )}

                  {/* Step 3: Payment Method */}
                  {currentStep === 3 && (
                    <Step3Payment
                      method={formData.payment_method}
                      onSelect={(method) =>
                        setFormData({ ...formData, payment_method: method })
                      }
                      notes={formData.notes}
                      onNotesChange={(notes) =>
                        setFormData({ ...formData, notes })
                      }
                    />
                  )}

                  {/* Step 4: Review Order */}
                  {currentStep === 4 && (
                    <Step4Review
                      cart={checkoutData.cart}
                      address={checkoutData.addresses.find(
                        a => a.id === formData.shipping_address_id
                      )}
                      shipping={checkoutData.shippingMethods.find(
                        m => m.id === formData.shipping_method_id
                      )}
                      payment={formData.payment_method}
                      totals={totals}
                    />
                  )}
                </AnimatePresence>

                {/* Navigation Buttons */}
                <div className="checkout-buttons">
                  <button
                    className="btn btn-outline-secondary"
                    onClick={handlePrevStep}
                    disabled={currentStep === 1 || loading}
                  >
                    ← Back
                  </button>

                  {currentStep < 4 ? (
                    <button
                      className="btn btn-primary"
                      onClick={handleNextStep}
                      disabled={loading}
                    >
                      {loading ? 'Validating...' : 'Continue →'}
                    </button>
                  ) : (
                    <motion.button
                      className="btn btn-success btn-lg"
                      onClick={handlePlaceOrder}
                      disabled={loading}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {loading ? 'Processing...' : '✓ Place Order'}
                    </motion.button>
                  )}
                </div>

                {/* Error Alert */}
                {error && (
                  <motion.div
                    className="alert alert-danger mt-3"
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                  >
                    {error}
                    <button
                      type="button"
                      className="btn-close"
                      onClick={() => setError(null)}
                    />
                  </motion.div>
                )}
              </motion.div>
            </div>

            {/* Right Column - Summary */}
            <div className="col-lg-4">
              <OrderSummary
                cart={checkoutData.cart}
                totals={totals}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// STEP 1: ADDRESS SELECTION
// ============================================================================

const Step1Address = ({ addresses, selected, onSelect }) => {
  return (
    <motion.div
      className="checkout-step"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <h3>Select Shipping Address</h3>

      <div className="address-list">
        {addresses && addresses.length > 0 ? (
          addresses.map((address) => (
            <motion.div
              key={address.id}
              className={`address-card ${selected === address.id ? 'selected' : ''}`}
              onClick={() => onSelect(address.id)}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <input
                type="radio"
                name="address"
                checked={selected === address.id}
                onChange={() => {}}
                style={{ cursor: 'pointer' }}
              />
              <div className="address-info">
                <h5>{address.full_name}</h5>
                <p>{address.street_address}</p>
                <p>
                  {address.city}, {address.state} {address.postal_code}
                </p>
                <p className="phone">📱 {address.phone_number}</p>
                {address.is_default && (
                  <span className="badge badge-primary">Default</span>
                )}
              </div>
            </motion.div>
          ))
        ) : (
          <p className="text-muted">No addresses found. Please add one first.</p>
        )}
      </div>

      <a href="/account/addresses" className="btn btn-outline-secondary btn-sm">
        + Add New Address
      </a>
    </motion.div>
  );
};

// ============================================================================
// STEP 2: SHIPPING METHOD
// ============================================================================

const Step2Shipping = ({ methods, selected, onSelect }) => {
  return (
    <motion.div
      className="checkout-step"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <h3>Select Shipping Method</h3>

      <div className="shipping-list">
        {methods && methods.length > 0 ? (
          methods.map((method) => (
            <motion.div
              key={method.id}
              className={`shipping-card ${selected === method.id ? 'selected' : ''}`}
              onClick={() => onSelect(method.id)}
              whileHover={{ scale: 1.02 }}
            >
              <input
                type="radio"
                name="shipping"
                checked={selected === method.id}
                onChange={() => {}}
              />
              <div className="shipping-info">
                <div className="shipping-header">
                  <h5>{method.name}</h5>
                  <span className="shipping-cost">৳{parseFloat(method.cost).toFixed(2)}</span>
                </div>
                <p className="shipping-delivery">
                  📦 Delivery in {method.delivery_days} day{method.delivery_days > 1 ? 's' : ''}
                </p>
                {method.description && (
                  <p className="shipping-description">{method.description}</p>
                )}
              </div>
            </motion.div>
          ))
        ) : (
          <p className="text-muted">No shipping methods available.</p>
        )}
      </div>
    </motion.div>
  );
};

// ============================================================================
// STEP 3: PAYMENT METHOD
// ============================================================================

const Step3Payment = ({ method, onSelect, notes, onNotesChange }) => {
  const paymentMethods = [
    {
      id: 'cod',
      name: 'Cash on Delivery',
      description: 'Pay when you receive your order',
      icon: '💵',
    },
    {
      id: 'bkash',
      name: 'bKash',
      description: 'Pay via bKash mobile wallet',
      icon: '📱',
    },
    {
      id: 'nagad',
      name: 'Nagad',
      description: 'Pay via Nagad',
      icon: '📱',
    },
    {
      id: 'card',
      name: 'Credit/Debit Card',
      description: 'Secure card payment',
      icon: '💳',
    },
  ];

  return (
    <motion.div
      className="checkout-step"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <h3>Select Payment Method</h3>

      <div className="payment-list mb-4">
        {paymentMethods.map((pm) => (
          <motion.div
            key={pm.id}
            className={`payment-card ${method === pm.id ? 'selected' : ''}`}
            onClick={() => onSelect(pm.id)}
            whileHover={{ scale: 1.02 }}
          >
            <input
              type="radio"
              name="payment"
              value={pm.id}
              checked={method === pm.id}
              onChange={() => {}}
            />
            <div className="payment-info">
              <span className="payment-icon">{pm.icon}</span>
              <div>
                <h5>{pm.name}</h5>
                <p>{pm.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="form-group">
        <label>Order Notes (Optional)</label>
        <textarea
          className="form-control"
          rows="4"
          placeholder="Add any special instructions for delivery..."
          value={notes}
          onChange={(e) => onNotesChange(e.target.value)}
        />
      </div>
    </motion.div>
  );
};

// ============================================================================
// STEP 4: REVIEW ORDER
// ============================================================================

const Step4Review = ({ cart, address, shipping, payment, totals }) => {
  const paymentMethodNames = {
    cod: 'Cash on Delivery',
    bkash: 'bKash',
    nagad: 'Nagad',
    card: 'Credit/Debit Card',
  };

  return (
    <motion.div
      className="checkout-step"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <h3>Review Your Order</h3>

      {/* Order Items */}
      <div className="review-section">
        <h5>Order Items</h5>
        <div className="review-items">
          {cart.items.map((item) => (
            <div key={item.id} className="review-item">
              <div className="item-details">
                <img src={item.product_image} alt={item.product_name} />
                <div>
                  <strong>{item.product_name}</strong>
                  {item.size && <p>Size: {item.size}</p>}
                  {item.color && <p>Color: {item.color}</p>}
                </div>
              </div>
              <div className="item-price">
                <span>x{item.quantity}</span>
                <strong>৳{(item.price * item.quantity).toFixed(2)}</strong>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Shipping Address */}
      {address && (
        <div className="review-section">
          <h5>Shipping To</h5>
          <p>
            <strong>{address.full_name}</strong><br />
            {address.street_address}<br />
            {address.city}, {address.state} {address.postal_code}<br />
            📱 {address.phone_number}
          </p>
        </div>
      )}

      {/* Shipping Method */}
      {shipping && (
        <div className="review-section">
          <h5>Shipping Method</h5>
          <p>
            <strong>{shipping.name}</strong> - ৳{parseFloat(shipping.cost).toFixed(2)}<br />
            <small>Estimated delivery: {shipping.delivery_days} day{shipping.delivery_days > 1 ? 's' : ''}</small>
          </p>
        </div>
      )}

      {/* Payment Method */}
      <div className="review-section">
        <h5>Payment Method</h5>
        <p>{paymentMethodNames[payment] || payment}</p>
      </div>
    </motion.div>
  );
};

// ============================================================================
// ORDER SUMMARY SIDEBAR
// ============================================================================

const OrderSummary = ({ cart, totals }) => {
  return (
    <motion.div
      className="order-summary sticky-top"
      style={{ top: '20px' }}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <h4>Order Summary</h4>

      {/* Items */}
      <div className="summary-items">
        {cart.items && cart.items.map((item) => (
          <div key={item.id} className="summary-item">
            <span>{item.product_name} x{item.quantity}</span>
            <span>৳{(item.price * item.quantity).toFixed(2)}</span>
          </div>
        ))}
      </div>

      <hr />

      {/* Totals */}
      <div className="summary-totals">
        <div className="summary-row">
          <span>Subtotal:</span>
          <span>৳{totals.subtotal}</span>
        </div>
        <div className="summary-row">
          <span>Shipping:</span>
          <span>৳{totals.shipping}</span>
        </div>
        <div className="summary-row">
          <span>Tax (5%):</span>
          <span>৳{totals.tax}</span>
        </div>
        {parseFloat(totals.discount) > 0 && (
          <div className="summary-row text-success">
            <span>Discount:</span>
            <span>-৳{totals.discount}</span>
          </div>
        )}
      </div>

      <hr />

      <div className="summary-total">
        <h5>Total Amount</h5>
        <div className="total-price">৳{totals.total}</div>
      </div>

      <div className="summary-info">
        <small>✓ Secure checkout</small>
        <small>✓ Free returns</small>
        <small>✓ 100% authentic</small>
      </div>
    </motion.div>
  );
};

export default CheckoutFlow;