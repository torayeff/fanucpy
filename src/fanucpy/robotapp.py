import traceback
from abc import ABC, abstractmethod


class RobotApp(ABC):
    """Generic Robot App Interface.
    Use this interface to develop robotic apps.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def configure(self):
        raise NotImplementedError("Should implement configure method!")

    @abstractmethod
    def _main(self, **kwargs):
        """Main method"""
        raise NotImplementedError("Should implement run method!")

    def run(self, **kwargs):
        """Execution method."""
        status = True
        message = "success"
        result = None
        try:
            result = self._main(**kwargs)
        except Exception as excp:
            status = False
            message = "".join(
                traceback.TracebackException.from_exception(excp).format()
            )
            result = None
        finally:
            return status, message, result
