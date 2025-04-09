from exceptions.app_exception import UserNotFoundError, UserAlreadyExistsError, InvalidCredentialsError
from repository.unit_of_work import UnitOfWork
from schemas.auth import AuthResponse

class UserService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

