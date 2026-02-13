import { useState, useCallback, useEffect } from 'react';

/**
 * Custom hook for user addresses
 * Manages saved addresses and selection
 */
export const useAddresses = () => {
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const API_BASE = '/api/v1';

    // Fetch all addresses for user
    const fetchAddresses = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/addresses/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Failed to fetch addresses');
            const data = await response.json();
            setAddresses(Array.isArray(data) ? data : data.results || []);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Add new address
    const addAddress = useCallback(async (addressData) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/addresses/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(addressData)
            });
            if (!response.ok) throw new Error('Failed to add address');
            const newAddress = await response.json();
            setAddresses(prev => [...prev, newAddress]);
            setError(null);
            return newAddress;
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Delete address
    const deleteAddress = useCallback(async (addressId) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/addresses/${addressId}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            if (!response.ok) throw new Error('Failed to delete address');
            setAddresses(prev => prev.filter(a => a.id !== addressId));
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchAddresses();
    }, [fetchAddresses]);

    return {
        addresses,
        loading,
        error,
        fetchAddresses,
        addAddress,
        deleteAddress
    };
};