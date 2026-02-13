/**
 * Cart Manager - Handles all cart operations
 * Production-ready with proper error handling
 */
class CartManager {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.cartCountElement = document.querySelector('[data-cart-count]');
        this.toastContainer = this.createToastContainer();
        this.init();
    }

    init() {
        this.attachEventListeners();
        this.updateCartCount();
    }

    attachEventListeners() {
        // Add to Cart
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action="add-to-cart"]');
            if (btn) {
                e.preventDefault();
                this.handleAddToCart(btn);
            }
        });

        // Add to Wishlist
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action="add-to-wishlist"]');
            if (btn) {
                e.preventDefault();
                this.handleAddToWishlist(btn);
            }
        });
    }

    async handleAddToCart(btn) {
        try {
            // Validate button
            if (!btn.dataset.productId) {
                this.showToast('Product ID missing', 'error');
                return;
            }

            const productId = btn.dataset.productId;
            const quantity = parseInt(btn.dataset.quantity) || 1;
            const size = btn.dataset.size || '';
            const color = btn.dataset.color || '';

            // Show loading state
            this.setButtonLoading(btn, true);

            // Make API request
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

            // Handle response
            if (!response.ok) {
                const error = await response.json();
                throw new Error(
                    error.detail || 
                    error.message || 
                    'Failed to add item to cart'
                );
            }

            const data = await response.json();

            // Success
            this.showToast('✓ Added to cart!', 'success');
            this.updateCartCount();
            this.animateCartIcon();

            // Dispatch custom event for other components
            window.dispatchEvent(new CustomEvent('cartUpdated', { detail: data }));

        } catch (error) {
            console.error('Add to cart error:', error);
            this.showToast(error.message || 'Failed to add item', 'error');
        } finally {
            this.setButtonLoading(btn, false);
        }
    }

    async handleAddToWishlist(btn) {
        try {
            if (!btn.dataset.productId) {
                this.showToast('Please log in', 'warning');
                return;
            }

            const productId = btn.dataset.productId;
            btn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/wishlist/add/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ product_id: productId }),
            });

            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = `/user/login/?next=${window.location.pathname}`;
                    return;
                }
                throw new Error('Failed to add to wishlist');
            }

            this.showToast('♥ Added to wishlist!', 'success');
            btn.classList.add('active');

        } catch (error) {
            console.error('Wishlist error:', error);
            this.showToast(error.message, 'error');
        } finally {
            btn.disabled = false;
        }
    }

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
                    this.cartCountElement.style.display = count > 0 ? 'inline-block' : 'none';
                }
            }
        } catch (error) {
            console.error('Error updating cart count:', error);
        }
    }

    setButtonLoading(btn, isLoading) {
        const spinner = btn.querySelector('.spinner-border');
        const text = btn.querySelector('.btn-text');

        if (isLoading) {
            btn.disabled = true;
            if (spinner) spinner.classList.remove('d-none');
            if (text) text.style.display = 'none';
        } else {
            btn.disabled = false;
            if (spinner) spinner.classList.add('d-none');
            if (text) text.style.display = 'inline';
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${message}</span>`;

        this.toastContainer.appendChild(toast);

        // Auto-remove
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    animateCartIcon() {
        const cartIcon = document.querySelector('[data-cart-icon]');
        if (cartIcon) {
            cartIcon.classList.add('bounce');
            setTimeout(() => cartIcon.classList.remove('bounce'), 600);
        }
    }

    createToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.cookie.split(';')
                   .find(c => c.trim().startsWith('csrftoken='))
                   ?.split('=')[1] || '';
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new CartManager());
} else {
    new CartManager();
}