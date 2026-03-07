import logging

from iteradraw.container import DependencyContainer
from iteradraw.core.infrastructure.buses.command_bus import CommandBus
from iteradraw.interfaces import CommandHandler
from iteradraw.log_config import configure_logger

"""
Bootstrapper for Iteradraw app. 

Usage
-----
Run this file directly to start the app:
    python bootstrap.py
"""

def main() -> None:
    configure_logger()
    container = DependencyContainer()
    build_command_pipeline(container)

def build_command_pipeline(container: DependencyContainer) -> None:
    command_bus = container.resolve(CommandBus)
    for handler_class in CommandHandler.__subclasses__():
        handler = container.resolve(handler_class)
        command_bus.register(
            command_type=handler.command_type,
            handler=handler.handle,
        )

if __name__ == "__main__":
    logger = logging.getLogger("iteradraw.bootstrap")
    logger.info("Application started")
    main()
    logger.info("Application finished")
