class ExternalApiError(Exception):
    """Ошибка с внешним API."""

    pass


class RelocationWithoutAreaError(Exception):
    """Ошибка связанная с указанием параметра relocation без area."""

    pass


class TextLogicError(Exception):
    """Ошибка связанная с некорректно настроенным фильтром по тексту."""

    pass


class TokenExpiredError(Exception):
    """Ошибка окончания действия токена."""

    pass
