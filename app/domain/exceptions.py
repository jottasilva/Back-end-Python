class DomainError(Exception):
    status_code = 400


class ReservationConflictError(DomainError):
    status_code = 409


class LocationConflictError(DomainError):
    status_code = 409


class ReservationForbiddenError(DomainError):
    status_code = 403


class ReservationNotFoundError(DomainError):
    status_code = 404
