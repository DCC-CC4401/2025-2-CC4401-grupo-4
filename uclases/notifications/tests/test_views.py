from django.urls import reverse
from notifications.models import Notification
from .test_base import NotificationBaseTests

class NotificationViewsTests(NotificationBaseTests):
    def setUp(self):
        super().setUp()
        self.url = reverse('notifications:list')

        self.notif_propia = Notification.objects.create(
            recipient=self.perfil_estudiante,
            type="NOTIFICATION_TEST_TYPE",
            title="Notificación Propia",
            message="Mensaje de Notificación Propia"
        )

        self.notif_ajena = Notification.objects.create(
            recipient=self.perfil_profe,
            type="NOTIFICATION_TEST_TYPE",
            title="Notificación Ajena",
            message="Mensaje de Notificación Ajena"
        )

        def test_notifications_list_view(self):
            self.client.force_login(self.estudiante)
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            n = response.context['notifications']

            self.assertEqual(len(n), 1)
            self.assertIn(self.notif_propia, n)
            self.assertNotIn(self.notif_ajena, n)
            
