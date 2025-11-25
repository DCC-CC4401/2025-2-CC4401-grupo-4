from django.urls import reverse
from notifications.models import Notification
from .test_base import NotificationBaseTests

class NotificationViewTest(NotificationBaseTests):
    
    def setUp(self):
        super().setUp()
        self.url = reverse('notifications:list')

    def test_view_content_with_notifications(self):
        """El usuario ve sus notificaciones listadas."""
        Notification.objects.create(
            receiver=self.perfil_estudiante, 
            type="generic_type", title="Tienes una notificación", message="Msg"
        )
        
        self.client.force_login(self.estudiante)
        resp = self.client.get(self.url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Tienes una notificación")
        self.assertEqual(len(resp.context['notifications']), 1)

    def test_view_empty_state(self):
        """Si no hay notificaciones, la vista no debe explotar."""
        self.client.force_login(self.estudiante)
        resp = self.client.get(self.url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['notifications']), 0)
        # Opcional: Si tienes un mensaje de "No hay notificaciones", testéalo aquí:
        # self.assertContains(resp, "No tienes notificaciones nuevas")

    def test_security_login_required(self):
        """Redirige al login si no está autenticado."""
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/')) # Ajusta según tu URL de login