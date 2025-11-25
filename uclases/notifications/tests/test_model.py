from notifications.models import Notification
from .test_base import NotificationBaseTests
from unittest.mock import MagicMock, patch

class NotificationModelTests(NotificationBaseTests):
    def test_create_notification(self):
        n = Notification.objects.create(
            receiver=self.perfil_estudiante,
            type="NOTIFICATION_TEST_TYPE",
            title = 'Titulo de Prueba',
            message = 'Mensaje de Prueba',
        )
        self.assertEqual(str(n), f"Titulo de Prueba - {self.perfil_estudiante.user.username}")
        self.assertFalse(n.read)
    @patch('notifications.models.NotificationStrategyFactory')
    def test_get_icon(self, mock_factory):
        mock_strategy = MagicMock()
        mock_strategy.get_icon.return_value = "test-icon"
        mock_factory.get_strategy.return_value = mock_strategy

        n = Notification.objects.create(
            receiver=self.perfil_estudiante,
            type="NOTIFICATION_TEST_TYPE",
            title = 'Título de Prueba',
            message = 'Mensaje de Prueba',
        )
        self.assertEqual(n.get_icon(), "test-icon")

