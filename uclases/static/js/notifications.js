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
                
                // Actualizar el botón "Marcar todas como leídas"
                updateMarkAllButton(data.unread_count);
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
            
            // Si ya está deshabilitado, no hacer nada
            if (button.disabled) {
                return;
            }
            
            button.disabled = true;
            const originalText = button.innerHTML;
            button.innerHTML = '<span>⏳</span><span>Marcando...</span>';
            
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
                    // Actualizar todas las tarjetas visualmente
                    const notificationCards = document.querySelectorAll('.notification-card');
                    notificationCards.forEach(card => {
                        // Quitar estilos de "no leída"
                        card.classList.remove('border-l-4', 'border-l-blue-500', 'bg-blue-50/50', 'dark:bg-blue-900/10');
                        
                        // Actualizar badge de cada notificación
                        const form = card.querySelector('.mark-notification-form');
                        if (form) {
                            const badgeButton = form.querySelector('button');
                            if (badgeButton) {
                                // Actualizar a estado "leída"
                                badgeButton.className = 'group px-2 py-1 text-xs font-medium bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 transition-colors';
                                badgeButton.innerHTML = `
                                    <span class="group-hover:hidden">Leída</span>
                                    <span class="hidden group-hover:inline">✕ Desmarcar</span>
                                `;
                                // Actualizar la URL del formulario para desmarcar
                                const notifId = form.action.match(/\/(\d+)\//)[1];
                                form.action = form.action.replace('/mark-read/', '/mark-unread/');
                            }
                        }
                    });
                    
                    // Actualizar contadores (esto también actualiza el botón)
                    updateUnreadCount(0);
                    updateMarkAllButton(0);
                } else {
                    // Restaurar el botón si falló
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al marcar todas como leídas');
                button.innerHTML = originalText;
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

/**
 * Actualiza el botón "Marcar todas como leídas" según el contador
 */
function updateMarkAllButton(count) {
    const markAllForm = document.getElementById('mark-all-read-form');
    if (!markAllForm) return;
    
    const button = markAllForm.querySelector('button');
    if (!button) return;
    
    if (count > 0) {
        // Activar botón
        button.disabled = false;
        button.className = 'px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white';
        button.removeAttribute('title');
        
        // Reconstruir contenido con badge
        button.innerHTML = `
            <span>✓</span>
            <span>Marcar todas como leídas</span>
            <span class="ml-1 px-2 py-0.5 bg-white/20 rounded-full text-xs font-bold">${count}</span>
        `;
    } else {
        // Desactivar botón
        button.disabled = true;
        button.className = 'px-4 py-2 rounded-lg font-medium text-sm transition-colors flex items-center gap-2 bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed';
        button.setAttribute('title', 'Todas las notificaciones están leídas');
        
        // Reconstruir contenido sin badge - texto diferente
        button.innerHTML = `
            <span>✓</span>
            <span>Todas leídas</span>
        `;
    }
}
