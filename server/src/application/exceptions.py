class ApplicationError(Exception):
    status_code: int
    detail: str

    def __init__(self, detail: str, status_code: int) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


class NotFoundError(ApplicationError):
    def __init__(self, detail: str = "Not found") -> None:
        super().__init__(detail=detail, status_code=404)


class ForbiddenError(ApplicationError):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(detail=detail, status_code=403)


class BadRequestError(ApplicationError):
    def __init__(self, detail: str = "Bad request") -> None:
        super().__init__(detail=detail, status_code=400)

