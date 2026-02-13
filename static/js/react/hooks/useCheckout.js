import { useState, useCallback } from 'react';
import { useCart } from './useCart';

/**
 * Custom hook for checkout process
 * Manages checkout state and validation
 */
export const useCheckout = (onError = null) => {
    const [checkoutData, setCheckoutData] = useState({
        cart_id: null,
        shipping_address_id: null,
        shipping_method_id: null,
        payment_method: 'cod',
        coupon_code: '',
        notes: ''
    });
    
    const [validationErrors, setValidationErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const { cart } = useCart();

    const API_BASE = '/api/v1';

    // Update checkout data
    const updateCheckout = useCallback((field, value) => {
        setCheckoutData(prev => ({
            ...prev,
            [field]: value
        }));
        // Clear error for this field
        setValidationErrors(prev => ({
            ...prev,
            [field]: null
        }));
    }, []);

    // Validate checkout data
    const validateCheckout = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/checkout/validate/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(checkoutData)
            });

            if (!response.ok) {
                const errors = await response.json();
                setValidationErrors(errors);
                return false;
            }

            const data = await response.json();
            return data.valid;
        } catch (err) {
            setValidationErrors({ general: err.message });
            if (onError) onError(err);
            return false;
        } finally {
            setLoading(false);
        }
    }, [checkoutData, onError]);

    // Confirm and create order
    const confirmCheckout = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/checkout/confirm/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(checkoutData)
            });

            if (!response.ok) {
                const errors = await response.json();
                setValidationErrors(errors);
                throw new Error('Checkout failed');
            }

            const order = await response.json();
            return order;
        } catch (err) {
            setValidationErrors({ general: err.message });
            if (onError) onError(err);
            return null;
        } finally {
            setLoading(false);
        }
    }, [checkoutData, onError]);

    return {
        checkoutData,
        validationErrors,
        loading,
        updateCheckout,
        validateCheckout,
        confirmCheckout
    };
};