/**
 * Script utama untuk aplikasi Kasir Smakta Resto
 */

// Format currency 
function formatCurrency(amount) {
    return 'Rp ' + Number(amount).toFixed(0).replace(/\d(?=(\d{3})+$)/g, '$&,');
}

// Format date in Indonesian format
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Show notification
function showNotification(message, type = 'success') {
    // Don't show success notifications as requested
    if (type === 'success') {
        return; // Skip creating notification for success messages
    }
    
    // Check if document.body exists
    if (!document.body) {
        console.error('Document body not available for notification');
        return;
    }
    
    try {
        // Ensure message is a string
        const safeMessage = String(message || '');
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification`;
        notification.textContent = safeMessage; // Use textContent instead of innerHTML for safety
        notification.style.position = 'fixed';
        notification.style.top = '70px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '250px';
        notification.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        
        // Add to body
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification && document.body.contains(notification)) {
                notification.style.opacity = '0';
                notification.style.transition = 'opacity 0.5s';
                setTimeout(() => {
                    // Use contains method to check if element is in the DOM
                    if (notification && document.body.contains(notification)) {
                        document.body.removeChild(notification);
                    }
                }, 500);
            }
        }, 3000);
    } catch (error) {
        console.error('Error showing notification:', error);
    }
}

// Check if element exists before adding event listener
function addEventListenerIfExists(elementId, eventType, callback) {
    const element = document.getElementById(elementId);
    if (element) {
        element.addEventListener(eventType, callback);
    }
}

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize any components that need to be setup
    initializeDatePickers();
    setupSearchFilters();
});

// Initialize date pickers if they exist
function initializeDatePickers() {
    // Set default dates for report filters
    const dateFromInput = document.getElementById('dateFrom');
    const dateToInput = document.getElementById('dateTo');
    
    if (dateToInput) {
        const today = new Date();
        const formattedToday = today.toISOString().split('T')[0];
        dateToInput.value = formattedToday;
        
        if (dateFromInput) {
            // Set date from to one week ago by default
            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(today.getDate() - 7);
            dateFromInput.value = oneWeekAgo.toISOString().split('T')[0];
        }
    }
}

// Setup search filters for tables
function setupSearchFilters() {
    // Product search
    addEventListenerIfExists('searchProduct', 'keyup', function(event) {
        if (event.key === 'Enter') {
            searchProducts();
        }
    });
    
    addEventListenerIfExists('btnSearch', 'click', searchProducts);
}

// Search products in product list
function searchProducts() {
    const searchInput = document.getElementById('searchProduct');
    
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    
    // Check if we're on products page
    const productTableBody = document.getElementById('productTableBody');
    if (productTableBody) {
        const rows = productTableBody.getElementsByTagName('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const productName = rows[i].getElementsByTagName('td')[1];
            
            if (productName) {
                const textValue = productName.textContent || productName.innerText;
                if (textValue.toLowerCase().indexOf(searchTerm) > -1) {
                    rows[i].style.display = "";
                } else {
                    rows[i].style.display = "none";
                }
            }
        }
    }
    
    // Check if we're on cashier page
    const productList = document.getElementById('productList');
    if (productList) {
        const products = productList.getElementsByClassName('product-item');
        
        for (let product of products) {
            const productName = product.getAttribute('data-name').toLowerCase();
            if (productName.includes(searchTerm)) {
                product.style.display = '';
            } else {
                product.style.display = 'none';
            }
        }
    }
}

// Low stock notification
function checkLowStock(threshold = 5) {
    const products = document.querySelectorAll('.stock-low');
    if (products.length > 0) {
        showNotification(`Perhatian: ${products.length} produk dengan stok rendah!`, 'warning');
    }
}

// Check for low stock when on products page
if (window.location.pathname.includes('products')) {
    setTimeout(checkLowStock, 1000);
}

// Filter sales by date range
function filterSales() {
    const dateFrom = document.getElementById('dateFrom').value;
    const dateTo = document.getElementById('dateTo').value;
    
    if (dateFrom && dateTo) {
        window.location.href = `/sales?from=${dateFrom}&to=${dateTo}`;
    } else {
        showNotification('Silakan pilih rentang tanggal dengan benar', 'danger');
    }
}