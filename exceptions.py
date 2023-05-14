class FalseTokensAndID(Exception):
    """Исключение на проверку токенов и ID пользователя."""

    pass


class SendMessageError(Exception):
    """Исключние свзанное с ошибкой при отправке сообщения."""

    pass


class NoInformationInHomework(Exception):
    """Исключение об отсувствии данных домашней работы."""

    pass


class TokensError(Exception):
    """Ошибка проверки токенов и ID."""

    pass
