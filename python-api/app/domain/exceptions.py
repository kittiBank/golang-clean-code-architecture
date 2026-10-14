"""Business errors raised by use cases and repositories.

They know nothing about HTTP; the API layer maps them to status codes (see app.core.errors).
"""


class DomainError(Exception):
    """Base class for all business rule errors."""


class AlreadyExistsError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass
