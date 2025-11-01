"""
Кастомные исключения для IQStocker v2.0
"""


class IQStockerException(Exception):
    """Базовое исключение для IQStocker"""
    pass


class UserNotFoundException(IQStockerException):
    """Пользователь не найден"""
    pass


class SubscriptionExpiredException(IQStockerException):
    """Подписка истекла"""
    pass


class LimitExceededException(IQStockerException):
    """Превышен лимит использования"""
    pass


class CSVValidationException(IQStockerException):
    """Ошибка валидации CSV файла"""
    pass


class ThemeGenerationException(IQStockerException):
    """Ошибка генерации темы"""
    pass


class PaymentException(IQStockerException):
    """Ошибка обработки платежа"""
    pass


class InsufficientPointsException(IQStockerException):
    """Недостаточно IQ баллов"""
    pass


class ReferralException(IQStockerException):
    """Ошибка реферальной программы"""
    pass

