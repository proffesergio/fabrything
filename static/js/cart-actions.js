/**
 * Cart Actions Module
 * Handles all cart interactions (add, remove, update, wishlist)
 * Works with both vanilla buttons and React components
 */

class CartManager {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.cartCountElement = document.querySelector('[data-cart-count]');
        this.wishlistCountElement = document.querySelector('[data-wishlist-count]');
        this.toastContainer = this.createToastContainer();
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.updateCartCount();
        this.updateWishlistCount();
    }

    attachEventListeners() {
        // Add to Cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-action="add-to-cart"]')) {
                e.preventDefault();
                const btn = e.target.closest('[data-action="add-to-cart"]');
                this.handleAddToCart(btn);
            }

            // Add to Wishlist buttons
            if (e.target.closest('[data-action="add-to-wishlist"]')) {
                e.preventDefault();
                const btn = e.target.closest('[data-action="add-to-wishlist"]');
                this.handleAddToWishlist(btn);
            }

            // Remove from Wishlist
            if (e.target.closest('[data-action="remove-from-wishlist"]')) {
                e.preventDefault();
                const btn = e.target.closest('[data-action="remove-from-wishlist"]');
                this.handleRemoveFromWishlist(btn);
            }
        });
    }

    /**
     * Handle Add to Cart
     */
    async handleAddToCart(btn) {
        try {
            const productId = btn.dataset.productId;
            const quantity = parseInt(btn.dataset.quantity || 1);
            const size = btn.dataset.size || '';
            const color = btn.dataset.color || '';

            if (!productId) {
                this.showToast('Product ID not found', 'error');
                return;
            }

            // Disable button and show loading state
            btn.disabled = true;
            const originalText = btn.innerHTML;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Adding...';

            const response = await fetch(`${this.apiBaseUrl}/cart/add_item/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity,
                    size: size,
                    color: color,
                }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to add item to cart');
            }

            const data = await response.json();

            // Show success message
            this.showToast('✓ Added to cart!', 'success');

            // Update cart count
            this.updateCartCount();

            // Dispatch custom event for React components
            window.dispatchEvent(new CustomEvent('cartUpdated', { detail: data }));

            // Animate cart icon
            this.animateCartIcon();

        } catch (error) {
            console.error('Add to cart error:', error);
            this.showToast(error.message || 'Failed to add item', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    /**
     * Handle Add to Wishlist
     */
    async handleAddToWishlist(btn) {
        try {
            const productId = btn.dataset.productId;

            if (!productId) {
                this.showToast('Please log in to save items', 'warning');
                return;
            }

            btn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/wishlist/add/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    product_id: productId,
                }),
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/user/login/?next=' + window.location.pathname;
                    return;
                }
                throw new Error('Failed to add to wishlist');
            }

            this.showToast('♥ Added to wishlist!', 'success');

            // Toggle button state
            btn.classList.add('active');
            btn.dataset.action = 'remove-from-wishlist';
            btn.innerHTML = '<i class="icon-heart-fill"></i>';

            // Update wishlist count
            this.updateWishlistCount();

        } catch (error) {
            console.error('Wishlist error:', error);
            this.showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
        }
    }

    /**
     * Handle Remove from Wishlist
     */
    async handleRemoveFromWishlist(btn) {
        try {
            const productId = btn.dataset.productId;
            btn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/wishlist/remove/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    product_id: productId,
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to remove from wishlist');
            }

            this.showToast('Removed from wishlist', 'info');

            // Toggle button state
            btn.classList.remove('active');
            btn.dataset.action = 'add-to-wishlist';
            btn.innerHTML = '<i class="icon-heart"></i>';

            // Update wishlist count
            this.updateWishlistCount();

        } catch (error) {
            console.error('Remove wishlist error:', error);
            this.showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
        }
    }

    /**
     * Update cart count in header
     */
    async updateCartCount() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/cart/current_cart/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });

            if (response.ok) {
                const data = await response.json();
                const count = data.items?.length || 0;

                if (this.cartCountElement) {
                    this.cartCountElement.textContent = count;
                    this.cartCountElement.style.display = count > 0 ? 'block' : 'none';
                }
            }
        } catch (error) {
            console.error('Error updating cart count:', error);
        }
    }

    /**
     * Update wishlist count in header
     */
    async updateWishlistCount() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/wishlist/`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });

            if (response.ok) {
                const data = await response.json();
                const count = data.length || 0;

                if (this.wishlistCountElement) {
                    this.wishlistCountElement.textContent = count;
                    this.wishlistCountElement.style.display = count > 0 ? 'block' : 'none';
                }
            }
        } catch (error) {
            console.error('Error updating wishlist count:', error);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span>${message}</span>
            </div>
        `;

        this.toastContainer.appendChild(toast);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Animate cart icon
     */
    animateCartIcon() {
        const cartIcon = document.querySelector('[data-cart-icon]');
        if (cartIcon) {
            cartIcon.classList.add('bounce');
            setTimeout(() => cartIcon.classList.remove('bounce'), 600);
        }
    }

    /**
     * Create toast container
     */
    createToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new CartManager();
    });
} else {
    new CartManager();
}