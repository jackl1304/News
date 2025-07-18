// Main JavaScript für Medizintechnik Newsletter

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialisiere Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialisiere Popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Fade-in Animation für Cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
    
    // Auto-hide Alerts nach 5 Sekunden
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Utility Functions
const Utils = {
    // Formatiere Datum
    formatDate: function(dateString) {
        if (!dateString) return 'Nicht verfügbar';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Zeige Loading Spinner
    showLoading: function(element) {
        const originalContent = element.innerHTML;
        element.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Lädt...';
        element.disabled = true;
        
        return function() {
            element.innerHTML = originalContent;
            element.disabled = false;
        };
    },
    
    // Zeige Toast Notification
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Entferne Toast nach dem Ausblenden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    },
    
    // Erstelle Toast Container
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    },
    
    // API Request Helper
    apiRequest: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },
    
    // Validiere E-Mail
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Escape HTML
    escapeHtml: function(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, function(m) { return map[m]; });
    }
};

// Form Validation
const FormValidator = {
    // Validiere Subscription Form
    validateSubscriptionForm: function(formData) {
        const errors = [];
        
        const email = formData.get('email');
        if (!email) {
            errors.push('E-Mail-Adresse ist erforderlich');
        } else if (!Utils.validateEmail(email)) {
            errors.push('Ungültige E-Mail-Adresse');
        }
        
        return errors;
    },
    
    // Zeige Validation Errors
    showValidationErrors: function(errors, formElement) {
        // Entferne vorherige Fehler
        const existingErrors = formElement.querySelectorAll('.invalid-feedback');
        existingErrors.forEach(error => error.remove());
        
        const inputs = formElement.querySelectorAll('.form-control');
        inputs.forEach(input => input.classList.remove('is-invalid'));
        
        // Zeige neue Fehler
        errors.forEach(error => {
            Utils.showToast(error, 'danger');
        });
    }
};

// Admin Dashboard Functions
const AdminDashboard = {
    // Aktualisiere Dashboard
    refreshDashboard: function() {
        location.reload();
    },
    
    // Lade Daten in Modal
    loadDataModal: async function(endpoint, title) {
        const modal = document.getElementById('dataModal');
        const modalTitle = document.getElementById('dataModalTitle');
        const modalBody = document.getElementById('dataModalBody');
        
        modalTitle.textContent = title;
        modalBody.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Lädt...</span>
                </div>
            </div>
        `;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        try {
            const data = await Utils.apiRequest(endpoint);
            
            // Erstelle Tabelle basierend auf Datentyp
            let tableHTML = '<div class="table-responsive"><table class="table table-striped">';
            
            if (data.length > 0) {
                // Header
                const headers = Object.keys(data[0]);
                tableHTML += '<thead><tr>';
                headers.forEach(header => {
                    tableHTML += `<th>${header}</th>`;
                });
                tableHTML += '</tr></thead>';
                
                // Body
                tableHTML += '<tbody>';
                data.forEach(item => {
                    tableHTML += '<tr>';
                    headers.forEach(header => {
                        let value = item[header];
                        if (typeof value === 'object' && value !== null) {
                            value = JSON.stringify(value);
                        }
                        if (typeof value === 'string' && value.length > 50) {
                            value = value.substring(0, 50) + '...';
                        }
                        tableHTML += `<td>${Utils.escapeHtml(String(value || ''))}</td>`;
                    });
                    tableHTML += '</tr>';
                });
                tableHTML += '</tbody>';
            } else {
                tableHTML += '<tbody><tr><td colspan="100%" class="text-center text-muted">Keine Daten verfügbar</td></tr></tbody>';
            }
            
            tableHTML += '</table></div>';
            modalBody.innerHTML = tableHTML;
            
        } catch (error) {
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Fehler beim Laden der Daten: ${error.message}
                </div>
            `;
        }
    },
    
    // Führe Admin-Aktion aus
    executeAdminAction: async function(endpoint, actionName, confirmMessage) {
        if (confirmMessage && !confirm(confirmMessage)) {
            return;
        }
        
        try {
            const result = await Utils.apiRequest(endpoint, { method: 'POST' });
            Utils.showToast(`${actionName} erfolgreich gestartet: ${result.message}`, 'success');
        } catch (error) {
            Utils.showToast(`Fehler bei ${actionName}: ${error.message}`, 'danger');
        }
    }
};

// Newsletter Functions
const Newsletter = {
    // Vorschau Newsletter
    previewNewsletter: function(newsletterId) {
        window.open(`/newsletter/${newsletterId}`, '_blank');
    },
    
    // Exportiere Newsletter
    exportNewsletter: function(newsletterId, format = 'html') {
        // Implementation für Newsletter Export
        Utils.showToast('Export-Funktionalität wird implementiert...', 'info');
    }
};

// Global Error Handler
window.addEventListener('error', function(event) {
    console.error('Global Error:', event.error);
    Utils.showToast('Ein unerwarteter Fehler ist aufgetreten', 'danger');
});

// Unhandled Promise Rejection Handler
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled Promise Rejection:', event.reason);
    Utils.showToast('Ein Fehler bei der Datenverarbeitung ist aufgetreten', 'danger');
});

// Expose global functions
window.Utils = Utils;
window.FormValidator = FormValidator;
window.AdminDashboard = AdminDashboard;
window.Newsletter = Newsletter;

