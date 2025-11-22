/**
 * Manejo de notificaciones con AJAX
 * Permite marcar como leída/no leída sin recargar la página
 */

document.addEventListener('DOMContentLoaded', function() {
    // Delegación de eventos para todos los formularios de marcar leída/no leída
    document.addEventListener('submit', function(e) {
        const form = e.target;
        
        // Solo interceptar formularios con la clase 'mark-notification-form'
        if (!form.classList.contains('mark-notification-form')) {
            return;
        }
        
        e.preventDefault();
        
        const url = form.action;
        const formData = new FormData(form);
        const button = form.querySelector('button');
        const notificationCard = form.closest('.notification-card');
        
        // Deshabilitar botón temporalmente
        button.disabled = true;
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar el estado del badge
                const isRead = data.is_read;
                
                // Actualizar la acción del formulario
                form.action = data.new_url;
                
                // Actualizar el contenido del botón
                if (isRead) {
                    button.className = 'group px-2 py-1 text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors';
                    button.innerHTML = `
                        <span class="group-hover:hidden">Leída</span>
                        <span class="hidden group-hover:inline">✕ Desmarcar</span>
                    `;
                    
                    // Quitar estilos de "no leída" de la tarjeta
                    notificationCard.classList.remove('border-l-4', 'border-l-blue-500', 'bg-blue-50/50', 'dark:bg-blue-900/10');
                } else {
                    button.className = 'px-2 py-1 text-xs font-bold bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors flex items-center gap-1';
                    button.innerHTML = `
                        <span class="inline-block w-1.5 h-1.5 bg-white rounded-full"></span>
                        Marcar como leída
                    `;
                    
                    // Agregar estilos de "no leída" a la tarjeta
                    notificationCard.classList.add('border-l-4', 'border-l-blue-500', 'bg-blue-50/50', 'dark:bg-blue-900/10');
                }
                
                // Actualizar contador si existe
                updateUnreadCount(data.unread_count);
            } else {
                alert(data.error || 'Error al actualizar la notificación');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al actualizar la notificación');
        })
        .finally(() => {
            button.disabled = false;
        });
    });
    
    // Marcar todas como leídas con AJAX
    const markAllForm = document.getElementById('mark-all-read-form');
    if (markAllForm) {
        markAllForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = this.action;
            const formData = new FormData(this);
            const button = this.querySelector('button');
            
            button.disabled = true;
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Recargar la página para mostrar todos los cambios
                    location.reload();
                } else {
                    alert(data.message || 'No hay notificaciones sin leer');
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al marcar todas como leídas');
                button.disabled = false;
            });
        });
    }
});

/**
 * Actualiza el contador de notificaciones no leídas (si existe en el navbar)
 */
function updateUnreadCount(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        if (count > 0) {
            badge.textContent = count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    }
}
