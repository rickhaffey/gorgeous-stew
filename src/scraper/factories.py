"""Factory base class for dynamic instantiation of objects."""

import importlib
from typing import Any


class FactoryBase:
    """
    Base class for all concrete Factory classes.

    Provides generic functionality for dynamically instantiating objects
    based on string names.
    """

    def instantiate(self, fqn: str) -> Any:  # noqa: ANN401
        """Instantiate an instance of a class dynamically based on the name provided."""
        name_components = fqn.split(".")
        class_name = name_components[-1]
        module_name = ".".join(name_components[:-1])

        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        return class_()
