import inspect
from typing import Type

"""
Dependency injection container for Iteradraw.

Defines the DI blocks for components of the application,
to be called by the bootstrapper at app initialization.
"""


class DependencyContainer:
    def __init__(self):
        self.registry = {}
        self.resolving = set()

    def resolve[T](self, object_type: Type[T]) -> T:
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
        object_parameters = inspect.signature(object_type).parameters.values()
        for parameter in object_parameters:
            parameter_class = parameter.annotation
            if not inspect.isclass(parameter_class):
                raise TypeError("Parameter type must be a class type")
            parameter_instance_map[parameter.name] = self.resolve(parameter_class)

        built_object = object_type(**parameter_instance_map,)
        return built_object