/**
 * Product Detail Page - Interactive Elements Handler
 * Manages color selection, size selection, quantity controls, and stock validation
 */

class ProductDetailPage {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.selectedColor = null;
        this.selectedSize = null;
        this.selectedQuantity = 1;
        this.maxStock = 0;
        this.init();
    }

    init() {
        this.cacheElements();
        this.attachEventListeners();
        this.updateAddToCartButton();
    }

    cacheElements() {
        // Color elements
        this.colorOptions = document.querySelectorAll('.color-option');
        this.productMainImage = document.getElementById('product-zoom');
        
        // Size & Stock elements
        this.sizeSelect = document.getElementById('size');
        this.qtyInput = document.getElementById('qty');
        this.qtyMinus = document.getElementById('qty-minus');
        this.qtyPlus = document.getElementById('qty-plus');
        
        // Buttons
        this.addToCartBtn = document.getElementById('addToCartBtn');
        this.wishlistBtn = document.getElementById('addToWishlistBtn');
        
        // Stock info
        this.stockStatus = document.querySelector('.stock-status');
        this.maxStock = parseInt(this.qtyInput?.dataset.maxStock) || 10;
    }

    attachEventListeners() {
        // Color selection
        if (this.colorOptions) {
            this.colorOptions.forEach(option => {
                option.addEventListener('click', (e) => this.handleColorChange(e));
            });
        }

        // Size selection
        if (this.sizeSelect) {
            this.sizeSelect.addEventListener('change', (e) => this.handleSizeChange(e));
        }

        // Quantity controls
        if (this.qtyMinus) {
            this.qtyMinus.addEventListener('click', () => this.decrementQuantity());
        }

        if (this.qtyPlus) {
            this.qtyPlus.addEventListener('click', () => this.incrementQuantity());
        }

        if (this.qtyInput) {
            this.qtyInput.addEventListener('input', (e) => this.handleQuantityInput(e));
            this.qtyInput.addEventListener('change', (e) => this.validateQuantity(e));
        }

        // Add to cart
        if (this.addToCartBtn) {
            this.addToCartBtn.addEventListener('click', () => this.handleAddToCart());
        }

        // Add to wishlist
        if (this.wishlistBtn) {
            this.wishlistBtn.addEventListener('click', (e) => this.handleAddToWishlist(e));
        }
    }

    /**
     * Handle color selection with image switching
     */
    handleColorChange(e) {
        e.preventDefault();
        const colorOption = e.currentTarget;
        
        // Remove active class from all color options
        this.colorOptions.forEach(opt => opt.classList.remove('active'));
        
        // Add active class to selected option
        colorOption.classList.add('active');
        
        // Get the image URL and update main product image
        const imageUrl = colorOption.dataset.image;
        if (imageUrl && this.productMainImage) {
            // Add fade effect
            this.productMainImage.style.opacity = '0.7';
            
            // Update image
            this.productMainImage.src = imageUrl;
            this.productMainImage.dataset.zoomImage = imageUrl;
            
            // Fade back in
            setTimeout(() => {
                this.productMainImage.style.opacity = '1';
            }, 300);
        }
        
        // Store selected color
        this.selectedColor = colorOption.title || colorOption.dataset.color || 'default';
        
        // Show subtle feedback
        this.showToast(`Color selected: ${this.selectedColor}`, 'info');
        this.updateAddToCartButton();
    }

    /**
     * Handle size selection
     */
    handleSizeChange(e) {
        this.selectedSize = e.target.value;
        
        if (this.selectedSize) {
            this.showToast(`Size selected: ${this.selectedSize}`, 'info');
        }
        
        this.updateAddToCartButton();
    }

    /**
     * Decrement quantity
     */
    decrementQuantity() {
        if (this.qtyInput) {
            let currentValue = parseInt(this.qtyInput.value) || 1;
            if (currentValue > 1) {
                currentValue--;
                this.qtyInput.value = currentValue;
                this.selectedQuantity = currentValue;
            }
        }
    }

    /**
     * Increment quantity
     */
    incrementQuantity() {
        if (this.qtyInput) {
            let currentValue = parseInt(this.qtyInput.value) || 1;
            if (currentValue < this.maxStock) {
                currentValue++;
                this.qtyInput.value = currentValue;
                this.selectedQuantity = currentValue;
            } else {
                this.showToast(`Maximum quantity is ${this.maxStock}`, 'warning');
            }
        }
    }

    /**
     * Handle quantity input
     */
    handleQuantityInput(e) {
        let value = parseInt(e.target.value) || 1;
        
        // Prevent negative values
        if (value < 1) {
            value = 1;
        }
        
        // Prevent exceeding stock
        if (value > this.maxStock) {
            value = this.maxStock;
        }
        
        e.target.value = value;
        this.selectedQuantity = value;
    }

    /**
     * Validate quantity on blur
     */
    validateQuantity(e) {
        let value = parseInt(e.target.value) || 1;
        
        if (value < 1) {
            value = 1;
            e.target.value = value;
            this.showToast('Quantity must be at least 1', 'warning');
        }
        
        if (value > this.maxStock) {
            value = this.maxStock;
            e.target.value = value;
            this.showToast(`Maximum quantity is ${this.maxStock}`, 'warning');
        }
        
        this.selectedQuantity = value;
    }

    /**
     * Update add to cart button state
     */
    updateAddToCartButton() {
        if (!this.addToCartBtn) return;
        
        // Button is enabled if stock is available
        // Size selection is optional for initial MVP
        const stockAvailable = this.maxStock > 0;
        
        if (stockAvailable) {
            this.addToCartBtn.disabled = false;
            this.addToCartBtn.style.opacity = '1';
            this.addToCartBtn.style.cursor = 'pointer';
        } else {
            this.addToCartBtn.disabled = true;
            this.addToCartBtn.style.opacity = '0.6';
            this.addToCartBtn.style.cursor = 'not-allowed';
        }
    }

    /**
     * Handle add to cart
     */
    async handleAddToCart() {
        try {
            // Get product ID from page context
            const productId = this.getProductId();
            if (!productId) {
                this.showToast('Product ID not found', 'error');
                return;
            }
            
            // Check if user is logged in
            if (!this.isUserLoggedIn()) {
                this.showToast('Please log in to add items to cart', 'warning');
                window.location.href = `/user/login/?next=${window.location.pathname}`;
                return;
            }
            
            // Disable button and show loading
            this.addToCartBtn.disabled = true;
            const originalHTML = this.addToCartBtn.innerHTML;
            this.addToCartBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            
            // Prepare request data
            const requestData = {
                product_id: productId,
                quantity: this.selectedQuantity,
                size: this.selectedSize || '',
                color: this.selectedColor || '',
            };
            
            // Make API call
            const response = await fetch(`${this.apiBaseUrl}/cart/add_item/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify(requestData),
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.message || 'Failed to add to cart');
            }
            
            const data = await response.json();
            
            // Success feedback
            this.showToast('✓ Successfully added to cart!', 'success');
            
            // Update cart UI if available
            this.updateCartCount();
            
            // Reset quantity after adding
            setTimeout(() => {
                this.qtyInput.value = 1;
                this.selectedQuantity = 1;
            }, 500);
            
            // Dispatch custom event for other listeners
            window.dispatchEvent(new CustomEvent('productAddedToCart', { detail: data }));
            
        } catch (error) {
            console.error('Add to cart error:', error);
            this.showToast(error.message || 'Failed to add to cart', 'error');
        } finally {
            // Re-enable button
            this.addToCartBtn.disabled = false;
            this.addToCartBtn.innerHTML = originalHTML;
        }
    }

    /**
     * Handle add to wishlist
     */
    async handleAddToWishlist(e) {
        e.preventDefault();
        
        try {
            if (!this.isUserLoggedIn()) {
                this.showToast('Please log in to add to wishlist', 'warning');
                window.location.href = `/user/login/?next=${window.location.pathname}`;
                return;
            }
            
            const productId = this.getProductId();
            if (!productId) {
                this.showToast('Product ID not found', 'error');
                return;
            }
            
            this.wishlistBtn.disabled = true;
            const originalHTML = this.wishlistBtn.innerHTML;
            this.wishlistBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            
            const response = await fetch(`${this.apiBaseUrl}/wishlist/add/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({ product_id: productId }),
            });
            
            if (response.status === 401) {
                window.location.href = `/user/login/?next=${window.location.pathname}`;
                return;
            }
            
            if (!response.ok) {
                throw new Error('Failed to add to wishlist');
            }
            
            this.showToast('♥ Added to wishlist!', 'success');
            this.wishlistBtn.classList.add('active');
            
        } catch (error) {
            console.error('Wishlist error:', error);
            this.showToast(error.message || 'Failed to add to wishlist', 'error');
        } finally {
            this.wishlistBtn.disabled = false;
            this.wishlistBtn.innerHTML = originalHTML;
        }
    }

    /**
     * Get product ID from page
     */
    getProductId() {
        // Try to get from data attribute first
        const productElement = document.querySelector('[data-product-id]');
        if (productElement) {
            return productElement.dataset.productId;
        }
        
        // Try to get from URL
        const urlPath = window.location.pathname;
        const match = urlPath.match(/product\/([^\/]+)/);
        if (match) {
            return match[1];
        }
        
        return null;
    }

    /**
     * Check if user is logged in
     */
    isUserLoggedIn() {
        return document.body.dataset.userId !== undefined || 
               document.querySelector('[data-user-logged-in]') !== null;
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
                
                const cartCountElement = document.querySelector('[data-cart-count]');
                if (cartCountElement) {
                    cartCountElement.textContent = count;
                    cartCountElement.style.display = count > 0 ? 'inline-block' : 'none';
                }
            }
        } catch (error) {
            console.error('Error updating cart count:', error);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${message}</span>`;
        
        container.appendChild(toast);
        
        // Auto remove
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Get CSRF token
     */
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               document.cookie.split(';')
                   .find(c => c.trim().startsWith('csrftoken='))
                   ?.split('=')[1] || '';
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new ProductDetailPage());
} else {
    new ProductDetailPage();
}
