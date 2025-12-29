"""Stardag: Declarative and composable DAG framework for Python.

Stardag provides a clean Python API for representing persistently stored assets
as a declarative Directed Acyclic Graph (DAG).

Basic usage::

    import stardag as sd

    @sd.task
    def get_range(limit: int) -> list[int]:
        return list(range(limit))

    @sd.task
    def get_sum(integers: sd.Depends[list[int]]) -> int:
        return sum(integers)

    task = get_sum(integers=get_range(limit=10))
    sd.build(task)
    print(task.output().load())  # 45

Core components:

- :func:`task` - Decorator for creating tasks from functions
- :class:`Task` - Base class for all tasks
- :class:`AutoTask` - Task with automatic filesystem targets
- :class:`Depends` - Dependency injection type annotation
- :func:`build` - Execute task and its dependencies

See https://docs.stardag.com for full documentation.

TODO: Expand docstrings for all public API components.
"""

from importlib.metadata import version

from pydantic import TypeAdapter

from stardag._auto_task import AutoTask
from stardag._base import (
    Task,
    TaskDeps,
    TaskIDRef,
    TaskStruct,
    auto_namespace,
    namespace,
)
from stardag._decorator import Depends, task
from stardag._parameter import IDHasher, IDHasherABC, IDHashInclude, IDHashIncludeABC
from stardag._task_parameter import TaskLoads, TaskParam, TaskSet
from stardag.build.registry import registry_provider
from stardag.build.sequential import build
from stardag.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    StardagError,
    TokenExpiredError,
)
from stardag.target import (
    DirectoryTarget,
    FileSystemTarget,
    LocalTarget,
    get_directory_target,
    get_target,
    target_factory_provider,
)

__version__ = version("stardag")

task_type_adapter = TypeAdapter(TaskParam[Task])
tasks_type_adapter = TypeAdapter(list[TaskParam[Task]])


__all__ = [
    "__version__",
    "APIError",
    "AuthenticationError",
    "AuthorizationError",
    "auto_namespace",
    "AutoTask",
    "build",
    "Depends",
    "DirectoryTarget",
    "FileSystemTarget",
    "get_directory_target",
    "get_target",
    "IDHasher",
    "IDHashInclude",
    "IDHasherABC",
    "IDHashIncludeABC",
    "LocalTarget",
    "namespace",
    "registry_provider",
    "StardagError",
    "Task",
    "TaskDeps",
    "TaskIDRef",
    "TaskLoads",
    "TaskParam",
    "TaskSet",
    "TaskStruct",
    "target_factory_provider",
    "task",
    "task_type_adapter",
    "tasks_type_adapter",
    "TokenExpiredError",
]
