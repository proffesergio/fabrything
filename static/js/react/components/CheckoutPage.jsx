import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import useCheckout from '../hooks/useCheckout';

const CheckoutPage = () => {
  const { checkoutData, order, loading, error, fetchCheckoutSummary, processCheckout } = useCheckout();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    shipping_address_id: null,
    shipping_method_id: null,
    payment_method: 'cod',
    coupon_code: '',
    notes: '',
  });

  useEffect(() => {
    fetchCheckoutSummary();
  }, []);

  const handleAddressSelect = (addressId) => {
    setFormData({ ...formData, shipping_address_id: addressId });
    setCurrentStep(2);
  };

  const handleShippingSelect = (methodId) => {
    setFormData({ ...formData, shipping_method_id: methodId });
    setCurrentStep(3);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await processCheckout(formData);
      // Redirect to order confirmation
      window.location.href = `/order-confirmation/${order.order_id}/`;
    } catch (err) {
      console.error('Checkout error:', err);
    }
  };

  if (order) {
    return (
      <motion.div
        className="container py-5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <div className="card border-0 shadow-sm">
          <div className="card-body text-center py-5">
            <h3 className="mb-3 text-success">✓ Order Placed Successfully!</h3>
            <p className="text-muted mb-4">
              Order ID: <strong>{order.order_id}</strong>
            </p>
            <a
              href={`/order-confirmation/${order.order_id}/`}
              className="btn btn-primary"
            >
              View Order Details
            </a>
          </div>
        </div>
      </motion.div>
    );
  }

  if (loading && !checkoutData) {
    return (
      <div className="container py-5">
        <div className="text-center">
          <div className="spinner-border" role="status" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="container py-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {error && (
        <div className="alert alert-danger mb-4">{error}</div>
      )}

      <div className="row">
        <div className="col-lg-8">
          <h2 className="mb-4">Checkout</h2>

          {/* Step Indicator */}
          <div className="mb-4">
            <div className="row text-center">
              {[1, 2, 3, 4].map((step) => (
                <div key={step} className="col">
                  <div
                    className={`rounded-circle d-inline-flex align-items-center justify-content-center mb-2 ${
                      currentStep >= step ? 'bg-primary' : 'bg-light'
                    }`}
                    style={{ width: '40px', height: '40px' }}
                  >
                    <span className={currentStep >= step ? 'text-white' : 'text-muted'}>
                      {step}
                    </span>
                  </div>
                  <div className="small">
                    {['Address', 'Shipping', 'Payment', 'Review'][step - 1]}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Step 1: Shipping Address */}
            {currentStep === 1 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h5 className="mb-3">Select Shipping Address</h5>
                {checkoutData?.addresses?.map((address) => (
                  <motion.div
                    key={address.id}
                    className="card mb-3 cursor-pointer"
                    onClick={() => handleAddressSelect(address.id)}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="card-body">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="radio"
                          name="address"
                          id={`address-${address.id}`}
                          value={address.id}
                          checked={formData.shipping_address_id === address.id}
                          onChange={() => {}}
                        />
                        <label
                          className="form-check-label w-100"
                          htmlFor={`address-${address.id}`}
                        >
                          <strong>{address.full_name}</strong>
                          <br />
                          {address.street_address}, {address.city}
                          <br />
                          <small className="text-muted">
                            {address.postal_code} • {address.phone_number}
                          </small>
                        </label>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {/* Step 2: Shipping Method */}
            {currentStep === 2 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h5 className="mb-3">Select Shipping Method</h5>
                {checkoutData?.shipping_methods?.map((method) => (
                  <motion.div
                    key={method.id}
                    className="card mb-3 cursor-pointer"
                    onClick={() => handleShippingSelect(method.id)}
                    whileHover={{ scale: 1.02 }}
                  >
                    <div className="card-body">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="radio"
                          name="shipping"
                          id={`shipping-${method.id}`}
                          value={method.id}
                          checked={formData.shipping_method_id === method.id}
                          onChange={() => {}}
                        />
                        <label
                          className="form-check-label w-100"
                          htmlFor={`shipping-${method.id}`}
                        >
                          <div className="d-flex justify-content-between">
                            <div>
                              <strong>{method.name}</strong>
                              <br />
                              <small className="text-muted">
                                {method.delivery_days} days delivery
                              </small>
                            </div>
                            <div className="text-end">
                              <strong>৳{method.cost}</strong>
                            </div>
                          </div>
                        </label>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}

            {/* Step 3: Payment Method */}
            {currentStep === 3 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h5 className="mb-3">Payment Method</h5>
                <div className="card mb-3">
                  <div className="card-body">
                    <div className="form-check mb-3">
                      <input
                        className="form-check-input"
                        type="radio"
                        id="cod"
                        name="payment"
                        value="cod"
                        checked={formData.payment_method === 'cod'}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            payment_method: e.target.value,
                          })
                        }
                      />
                      <label className="form-check-label" htmlFor="cod">
                        Cash on Delivery (COD)
                      </label>
                      <small className="text-muted d-block ms-4">
                        Pay when you receive your order
                      </small>
                    </div>
                  </div>
                </div>

                <h5 className="mb-3 mt-4">Order Notes (Optional)</h5>
                <div className="mb-3">
                  <textarea
                    className="form-control"
                    rows="3"
                    placeholder="Any special instructions for delivery..."
                    value={formData.notes}
                    onChange={(e) =>
                      setFormData({ ...formData, notes: e.target.value })
                    }
                  />
                </div>

                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={() => setCurrentStep(4)}
                >
                  Continue to Review
                </button>
              </motion.div>
            )}

            {/* Step 4: Review & Confirm */}
            {currentStep === 4 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <h5 className="mb-3">Review Your Order</h5>
                
                <div className="card mb-3">
                  <div className="card-body">
                    <h6>Order Items</h6>
                    {checkoutData?.cart?.items?.map((item) => (
                      <div key={item.id} className="d-flex justify-content-between mb-2">
                        <span>{item.product_title} x{item.quantity}</span>
                        <span>৳{item.total_price}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card mb-3">
                  <div className="card-body">
                    <h6>Pricing</h6>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Subtotal:</span>
                      <span>৳{checkoutData?.cart?.subtotal}</span>
                    </div>
                    <div className="d-flex justify-content-between mb-2">
                      <span>Shipping:</span>
                      <span>
                        ৳
                        {checkoutData?.shipping_methods?.find(
                          (m) => m.id === formData.shipping_method_id
                        )?.cost || 0}
                      </span>
                    </div>
                    <hr />
                    <div className="d-flex justify-content-between">
                      <strong>Total:</strong>
                      <strong className="text-primary fs-5">
                        ৳
                        {(
                          parseFloat(checkoutData?.cart?.subtotal || 0) +
                          parseFloat(
                            checkoutData?.shipping_methods?.find(
                              (m) => m.id === formData.shipping_method_id
                            )?.cost || 0
                          )
                        ).toFixed(2)}
                      </strong>
                    </div>
                  </div>
                </div>

                <motion.button
                  type="submit"
                  className="btn btn-success btn-lg w-100"
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {loading ? 'Processing...' : 'Place Order'}
                </motion.button>
              </motion.div>
            )}
          </form>
        </div>

        {/* Order Summary Sidebar */}
        <div className="col-lg-4">
          <motion.div
            className="card shadow-sm sticky-top"
            style={{ top: '20px' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="card-body">
              <h5 className="card-title mb-3">Order Summary</h5>
              {checkoutData?.cart?.items?.map((item) => (
                <div key={item.id} className="mb-2 small">
                  <div className="d-flex justify-content-between">
                    <span>{item.product_title}</span>
                    <span>x{item.quantity}</span>
                  </div>
                  <div className="d-flex justify-content-between text-muted">
                    <span>৳{item.product_price}</span>
                    <span>৳{item.total_price}</span>
                  </div>
                </div>
              ))}
              <hr />
              <div className="d-flex justify-content-between mb-2">
                <span>Subtotal:</span>
                <span>৳{checkoutData?.cart?.subtotal}</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Shipping:</span>
                <span>
                  ৳
                  {checkoutData?.shipping_methods?.find(
                    (m) => m.id === formData.shipping_method_id
                  )?.cost || '0.00'}
                </span>
              </div>
              <hr />
              <div className="d-flex justify-content-between">
                <strong>Total:</strong>
                <strong className="text-primary fs-5">
                  ৳
                  {(
                    parseFloat(checkoutData?.cart?.subtotal || 0) +
                    parseFloat(
                      checkoutData?.shipping_methods?.find(
                        (m) => m.id === formData.shipping_method_id
                      )?.cost || 0
                    )
                  ).toFixed(2)}
                </strong>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default CheckoutPage;