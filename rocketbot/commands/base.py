import abc  # Abstract Base Class
from typing import List

import rocketbot.models as m


class BaseCommand(abc.ABC):
    @abc.abstractmethod
    def usage(self) -> List[str]:
        pass

    @abc.abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check whether the command is applicable
        """
        pass

    @abc.abstractmethod
    async def handle(self, command: str, args: str, message: m.Message) -> None:
        """Handle the incoming message
        """
        pass
