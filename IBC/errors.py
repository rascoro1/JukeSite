class InvalidFindSlaveArgumentException(Exception):
    def __init__(self, message, errors):
            super(InvalidFindSlaveArgumentException, self).__init__(message)
            self.errors = errors


class SlaveIsNotActiveException(Exception):
    def __init__(self, message, errors):
            super(SlaveIsNotActiveException, self).__init__(message)
            self.errors = errors

class DaemonIsAlreadyActive(Exception):
    def __init__(self, message, errors):
            super(DaemonIsAlreadyActive, self).__init__(message)
            self.errors = errors

class MobileClientNotInitError(Exception):
    def __init__(self, message, errors):
            super(MobileClientNotInitError, self).__init__(message)
            self.errors = errors

class SessionNotActive(Exception):
    def __init__(self, message, errors):
            super(SessionNotActive, self).__init__(message)
            self.errors = errors

class CannotDownloadSongError(Exception):
    def __init__(self, message, errors):
            super(CannotDownloadSongError, self).__init__(message)
            self.errors = errors

class SetIpAddressError(Exception):
    def __init__(self, message, errors):
            super(SetIpAddressError, self).__init__(message)
            self.errors = errors

class SetInterfaceError(Exception):
    def __init__(self, message, errors):
            super(SetInterfaceError, self).__init__(message)
            self.errors = errors

class CouldNotOpenIBCConfigFile(Exception):
    def __init__(self, message, errors):
            super(CouldNotOpenIBCConfigFile, self).__init__(message)
            self.errors = errors


class CouldNotLoginError(Exception):
    def __init__(self, message, errors):
            super(CouldNotLoginError, self).__init__(message)
            self.errors = errors


class SongAlreadyDownloadedException(Exception):
    def __init__(self, message, errors):
            super(SongAlreadyDownloadedException, self).__init__(message)
            self.errors = errors


class SongIsNotDownloadedError(Exception):
    def __init__(self, message, errors):
            super(SongIsNotDownloadedError, self).__init__(message)
            self.errors = errors





