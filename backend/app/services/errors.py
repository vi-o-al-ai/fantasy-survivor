"""Errors raised by services. The HTTP layer maps them to status codes."""


class NotFoundError(Exception):
    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(f"{entity} {identifier!r} not found")
        self.entity = entity
        self.identifier = identifier


class ForbiddenError(Exception):
    """The caller is authenticated but not allowed to do this."""


class RuleViolationError(Exception):
    """A request was well-formed but breaks a league rule (e.g. draft closed)."""
