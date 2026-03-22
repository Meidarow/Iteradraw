import inspect
from typing import Type, get_type_hints

"""
Dependency injection container for Iteradraw.

Defines the DI blocks for components of the application,
to be called by the bootstrapper at app initialization.
"""


class DependencyContainer:
    def __init__(self):
        self.registry = {}
        self.default_concretes = {}
        self.resolving = set()

    def resolve[T](self, object_type: "Type[T]") -> T:
        if object_type in self.registry:
            return self.registry[object_type]

        if object_type in self.resolving:
            raise TypeError(
                f"Circular resolution of dependency {object_type} detected.")

        self.resolving.add(object_type)
        built_object = self.generic_factory(object_type)
        self.resolving.remove(object_type)
        self.registry[object_type] = built_object
        return built_object

    def generic_factory(self, object_type):
        parameter_instance_map = {}
        if inspect.isabstract(object_type):
            object_type = self.default_concretes[object_type]
        parameters = get_type_hints(object_type.__init__).items()
        for name, cls in parameters:
            if name == "return":
                continue
            if not inspect.isclass(cls):
                raise TypeError("Parameter type must be a class type")
            parameter_instance_map.setdefault(
                name,
                self.resolve(cls)
            )

        built_object = object_type(**parameter_instance_map,)
        return built_object