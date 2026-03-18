from iteradraw.bootstrap import register_default_concrete_classes, \
    build_command_handlers, register_command_handlers, ALL_HANDLERS
from iteradraw.container import DependencyContainer
from iteradraw.core.infrastructure.buses.command_bus import CommandBus


class TestDependencyContainer:
    def test_command_registration(self):
        container = DependencyContainer()
        register_default_concrete_classes(container)
        command_bus = container.resolve(CommandBus)
        handler_instances = build_command_handlers(container)
        register_command_handlers(command_bus, handler_instances)
        for handler_cls in ALL_HANDLERS:
            assert handler_cls.command_type in command_bus.handler_map
