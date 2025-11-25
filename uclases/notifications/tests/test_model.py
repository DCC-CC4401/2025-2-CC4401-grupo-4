from notifications.models import Notification
from unittest.mock import patch, MagicMock
from .test_base import NotificationBaseTests

class NotificationModelTests(NotificationBaseTests):
    
    def test_create_notification_defaults(self):
        """Prueba que los valores por defecto (read=False, timestamps) se asignen bien."""
        notif = Notification.objects.create(
            receiver=self.perfil_estudiante, 
            type="generic_type",
            title="Hola",
            message="Mundo"
        )
        
        self.assertFalse(notif.read) # Default debe ser False
        self.assertIsNotNone(notif.creation_date) # Debe tener fecha
        self.assertIsNone(notif.action_taken) # Default None
        
        # Prueba del método __str__
        expected_str = f"Hola - {self.perfil_estudiante.user.username}"
        self.assertEqual(str(notif), expected_str)

    @patch('notifications.models.NotificationStrategyFactory')
    def test_model_delegates_to_strategy(self, mock_factory):
        """Prueba que el modelo sabe pedir íconos y acciones a su estrategia."""
        
        # Mock Strategy
        mock_strategy = MagicMock()
        mock_strategy.get_icon.return_value = "🔔"
        mock_strategy.get_actions.return_value = [{"label": "Ver"}]
        mock_factory.get_strategy.return_value = mock_strategy

        notif = Notification.objects.create(
            receiver=self.perfil_estudiante,
            type="test_delegation", 
            title="T", message="M"
        )
        
        # 1. Test Icon
        self.assertEqual(notif.get_icon(), "🔔")
        mock_factory.get_strategy.assert_called_with("test_delegation")
        
        # 2. Test Actions
        actions = notif.get_available_actions()
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['label'], "Ver")