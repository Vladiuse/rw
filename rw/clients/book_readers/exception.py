from common.exception import ApplicationException


class ContainerFileReadError(ApplicationException):
    pass

class ContainerNotFound(ContainerFileReadError):
    pass

class FileLineFindDataError(ContainerFileReadError):
    pass