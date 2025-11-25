from notifications.services.notification_service import NotificationService
from notifications.models import Notification
from .test_base import NotificationBaseTests

class NotificationServicetest(NotificationBaseTests):
    def test_send_notification(self):
        data = {"dato": "valor"}
        NotificationService.send(
            receiver=self.perfil_estudiante,
            type="NOTIFICATION_TEST_TYPE",
            data=data
        )
        self.assertEqual(Notification.objects.count(), 1)
        n = Notification.objects.first()

        self.assertEqual(n.title, "Título Test")
        self.assertEqual(n.message, "Mensaje Test")
        self.assertEqual(n.type, "NOTIFICATION_TEST_TYPE")