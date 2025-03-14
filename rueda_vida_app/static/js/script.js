// Función para confirmar eliminación
function confirmarEliminar(mensaje) {
    return confirm(mensaje || '¿Estás seguro de que deseas eliminar este elemento?');
}

// Función para mostrar alertas temporales
function mostrarAlerta(mensaje, tipo) {
    const alertPlaceholder = document.getElementById('alertPlaceholder') || document.createElement('div');
    
    if (!document.getElementById('alertPlaceholder')) {
        alertPlaceholder.id = 'alertPlaceholder';
        alertPlaceholder.className = 'position-fixed top-0 end-0 p-3';
        document.body.appendChild(alertPlaceholder);
    }
    
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
        <div class="alert alert-${tipo || 'info'} alert-dismissible fade show" role="alert">
            ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertPlaceholder.appendChild(wrapper);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        const alert = wrapper.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Inicializar tooltips de Bootstrap
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips si Bootstrap está cargado
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Actualizar año en el footer
    const yearElement = document.getElementById('current-year');
    if (yearElement) {
        yearElement.textContent = new Date().getFullYear();
    }
});