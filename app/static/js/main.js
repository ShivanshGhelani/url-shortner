// Universal URL Shortener - Custom JavaScript

// Enhanced copy to clipboard with visual feedback
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        const originalHTML = button.innerHTML;
        const originalClasses = button.className;
        
        // Update button to show success
        button.innerHTML = '<i class="fas fa-check mr-1"></i> Copied!';
        button.className = button.className.replace(/bg-\w+-\d+/, 'bg-green-500');
        button.className = button.className.replace(/hover:bg-\w+-\d+/, 'hover:bg-green-600');
        
        // Reset after 2 seconds
        setTimeout(function() {
            button.innerHTML = originalHTML;
            button.className = originalClasses;
        }, 2000);
    }).catch(function(err) {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy to clipboard');
    });
}

// Enhanced password toggle with icon animation
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.querySelector(`[onclick="togglePassword('${inputId}')"] i`);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
        icon.style.color = '#3b82f6';
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
        icon.style.color = '';
    }
}

// Auto-dismiss alerts with fade animation
function initAlerts() {
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

// URL validation for forms
function validateURL(url) {
    try {
        new URL(url);
        return true;
    } catch (e) {
        return false;
    }
}

// Real-time URL validation
function initURLValidation() {
    const urlInputs = document.querySelectorAll('input[type="url"]');
    urlInputs.forEach(input => {
        input.addEventListener('input', function() {
            const url = this.value.trim();
            if (url && !validateURL(url)) {
                this.classList.add('border-red-500', 'ring-red-500');
                this.classList.remove('border-gray-300', 'ring-blue-500');
            } else {
                this.classList.remove('border-red-500', 'ring-red-500');
                this.classList.add('border-gray-300');
            }
        });
    });
}

// Loading button states
function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        const originalHTML = button.innerHTML;
        button.dataset.originalHTML = originalHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalHTML || button.innerHTML;
    }
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Format numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Time ago formatter
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, seconds] of Object.entries(intervals)) {
        const interval = Math.floor(diffInSeconds / seconds);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'Just now';
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            showTooltip(this, this.dataset.tooltip);
        });
        
        element.addEventListener('mouseleave', function() {
            hideTooltip();
        });
    });
}

function showTooltip(element, text) {
    const tooltip = document.createElement('div');
    tooltip.id = 'tooltip';
    tooltip.className = 'absolute z-50 px-2 py-1 text-sm text-white bg-gray-900 rounded shadow-lg';
    tooltip.textContent = text;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
    tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Keyboard shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search/URL input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const urlInput = document.getElementById('long_url');
            if (urlInput) {
                urlInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal, [id*="Modal"]');
            modals.forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.classList.remove('flex');
                }
            });
        }
    });
}

// Download file helper
function downloadFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Share API fallback
function shareContent(title, text, url) {
    if (navigator.share) {
        navigator.share({
            title: title,
            text: text,
            url: url
        }).catch(err => console.log('Error sharing:', err));
    } else {
        // Fallback to clipboard
        const shareText = `${title}\n${text}\n${url}`;
        copyToClipboard(shareText);
        alert('Content copied to clipboard!');
    }
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initAlerts();
    initURLValidation();
    initTooltips();
    initKeyboardShortcuts();
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.style.opacity = '0';
        mainContent.style.transform = 'translateY(20px)';
        setTimeout(() => {
            mainContent.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            mainContent.style.opacity = '1';
            mainContent.style.transform = 'translateY(0)';
        }, 100);
    }
    
    console.log('🔗 Universal URL Shortener initialized successfully!');
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Note: Service worker file would need to be created
        // navigator.serviceWorker.register('/sw.js');
    });
}
