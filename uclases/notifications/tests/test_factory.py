from notifications.strategy.factory import NotificationStrategyFactory
from notifications.strategy.fallback import NotificationStrategyFallback
from .test_base import NotificationBaseTests, TestStrategyBase 

class NotificationFactoryTests(NotificationBaseTests):
    def test_registered_strategy(self):
        strategy = NotificationStrategyFactory.get_strategy("NOTIFICATION_TEST_TYPE")
        self.assertIsInstance(strategy, TestStrategyBase)
        self.assertEqual(strategy.get_icon(), "test-icon")

    def test_fallback_strategy(self):
        strategy = NotificationStrategyFactory.get_strategy("key_inexistente_x")
        self.assertIsInstance(strategy, NotificationStrategyFallback)