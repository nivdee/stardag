# Stardag Repository Architecture Analysis

**Analysis Date:** January 8, 2026
**Analyzed by:** Claude (Opus 4.5)
**Repository:** nivdee/stardag

---

## Executive Summary

Stardag is a **declarative and composable DAG (Directed Acyclic Graph) framework** for Python with persistent asset management. It provides a sophisticated task execution system with:

- **Type-safe task definitions** using Pydantic
- **Deterministic output paths** based on parameter hashing
- **Bottom-up execution** (Makefile-style build system)
- **Multi-tier API** (decorator, AutoTask, base Task class)
- **Extensible storage** (local filesystem, S3, Modal volumes)
- **Cloud integrations** (Prefect orchestration, Modal serverless)
- **Enterprise registry service** (multi-tenant task tracking)

---

## Table of Contents

1. [Core Architecture](#core-architecture)
2. [Key Components](#key-components)
3. [Branch Analysis](#branch-analysis)
4. [Code Quality Assessment](#code-quality-assessment)
5. [Design Patterns](#design-patterns)
6. [Technology Stack](#technology-stack)

---

## Core Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER CODE                                      │
│                                                                          │
│   @task decorator  →  AutoTask class  →  Task base class                │
│   (simple)            (mid-level)        (full control)                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                       TASK SYSTEM                                        │
│                                                                          │
│   Task Definition  →  Dependency Resolution  →  Build Execution         │
│   (Pydantic)          (DAG traversal)           (Bottom-up)             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                      TARGET SYSTEM                                       │
│                                                                          │
│   LocalTarget  │  S3Target  │  ModalVolumeTarget  │  InMemoryTarget     │
│       ▼             ▼              ▼                    ▼                │
│   Serializers: JSON │ Pickle │ CSV │ PlainText │ Custom                 │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                    INTEGRATIONS                                          │
│                                                                          │
│   Prefect (Orchestration)  │  Modal (Serverless)  │  AWS S3 (Storage)   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Concepts

| Concept        | Description                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------- |
| **Task**       | A Pydantic model representing a unit of work with inputs (parameters) and outputs (targets) |
| **Target**     | Abstraction for persistent storage (local file, S3 object, Modal volume)                    |
| **Build**      | Bottom-up DAG execution - only runs tasks whose outputs don't exist                         |
| **Task ID**    | Deterministic hash of namespace + family + parameters (SHA1)                                |
| **Serializer** | Converts Python objects to/from persistent storage format                                   |

---

## Key Components

### 1. Task System (`src/stardag/`)

#### Three-Level API

| Level         | Class/Decorator   | Use Case                                      | Control Level |
| ------------- | ----------------- | --------------------------------------------- | ------------- |
| **Simple**    | `@task` decorator | Quick task definitions, functional style      | Low           |
| **Mid-level** | `AutoTask[T]`     | Automatic filesystem targets with type safety | Medium        |
| **Full**      | `Task[TargetT]`   | Maximum flexibility, custom targets           | High          |

#### Core Files

| File                 | Lines | Purpose                                       |
| -------------------- | ----- | --------------------------------------------- |
| `_base.py`           | ~425  | Core Task class, registration, ID hashing     |
| `_decorator.py`      | ~183  | `@task` decorator implementation              |
| `_auto_task.py`      | ~77   | AutoTask with automatic path generation       |
| `_task_parameter.py` | ~142  | TaskLoads, TaskSet, TaskParam types           |
| `_parameter.py`      | ~100  | IDHasher, IDHashInclude for parameter control |

#### Key Design Decisions

1. **Pydantic Integration**: All tasks are Pydantic BaseModel instances
   - Full validation and serialization
   - JSON schema generation
   - IDE support via type hints

2. **Parameter-Based Hashing**: Task ID = SHA1(namespace, family, parameters)
   - Enables deterministic output paths
   - Supports incremental builds
   - Parameters can be excluded via `IDHashExclude`

3. **Composition Model**: Tasks as first-class parameters
   - `TaskLoads[T]` for type-safe dependencies
   - `TaskSet` for variable-length task collections
   - Recursive serialization of nested tasks

### 2. Target System (`src/stardag/target/`)

#### Protocol Hierarchy

```python
Target (base)
├── LoadableTarget[T]      # Can load() → T
├── SaveableTarget[T]      # Can save(T)
├── LoadableSaveableTarget[T]
└── FileSystemTarget       # File I/O operations
    ├── LocalTarget        # Local filesystem
    ├── RemoteFileSystemTarget  # S3, Modal volumes
    └── DirectoryTarget    # Multi-file outputs
```

#### Serialization

| Serializer                     | Extension | Type                  | Use Case                     |
| ------------------------------ | --------- | --------------------- | ---------------------------- |
| `JSONSerializer`               | `.json`   | Any JSON-serializable | Default for structured data  |
| `PlainTextSerializer`          | `.txt`    | `str`                 | Plain text files             |
| `PickleSerializer`             | `.pkl`    | Any                   | Fallback for complex objects |
| `PandasDataFrameCSVSerializer` | `.csv`    | DataFrame             | Tabular data                 |
| `SelfSerializer`               | Custom    | Protocol-implementing | Custom serialization         |

#### Atomic Writes

All file operations use atomic write pattern:

1. Write to temporary file (`.tmp-{uuid7}`)
2. Atomic rename on success
3. Cleanup on failure

### 3. Build System (`src/stardag/build/`)

| File             | Purpose                             |
| ---------------- | ----------------------------------- |
| `sequential.py`  | Single-threaded DAG executor        |
| `task_runner.py` | Task execution with hooks           |
| `registry.py`    | Filesystem-based execution registry |

#### Execution Flow

```
build(task)
    │
    ▼
is_complete(task)?  ──Yes──▶  Return (skip)
    │
    No
    ▼
for dep in task.deps():
    build(dep)  ◀──────────── Recursive
    │
    ▼
task_runner.run(task)
    │
    ▼
registry.register(task)
```

### 4. Integrations (`src/stardag/integration/`)

#### Prefect Integration

- Converts stardag DAGs to Prefect flows
- Async execution with `PrefectConcurrentFuture`
- Artifact creation for task metadata
- Dynamic dependency support

#### Modal Integration

- `StardagApp` wrapper for Modal deployment
- Multiple worker types with resource configuration
- Volume-based persistent storage
- Optional Prefect integration for observability

#### AWS S3 Integration

- `S3FileSystem` implementing `RemoteFileSystemABC`
- Optional local caching via `CachedRemoteFileSystem`
- Automatic target routing via URI prefix (`s3://`)

---

## Branch Analysis

### Main Branch (Current)

**Purpose**: Core stardag framework
**Components**: Task system, targets, build, integrations
**Status**: Stable, production-ready

### `registry-service` Branch

**Purpose**: Centralized task registry service
**Scope**: ~50,000 lines added
**Architecture**:

```
┌──────────────────────────────────────────────────────────────┐
│              Registry Service Architecture                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │  React UI   │◀──▶│ FastAPI API │◀──▶│ PostgreSQL  │     │
│   │  Port 3000  │    │  Port 8000  │    │  Port 5432  │     │
│   └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                               │
│   Features:                                                   │
│   • Multi-tenant (organizations, workspaces)                 │
│   • OIDC authentication (Keycloak, Cognito)                  │
│   • API key support for CI/CD                                │
│   • Build tracking and task registry                         │
│   • Web dashboard with DAG visualization                     │
│   • AWS CDK infrastructure templates                         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key Additions**:

- `app/stardag-api/` - FastAPI backend (6 route modules, SQLAlchemy models)
- `app/stardag-ui/` - React TypeScript frontend
- `lib/stardag/cli/` - CLI commands for auth/config
- `infra/aws-cdk/` - AWS deployment infrastructure
- `integration-tests/` - E2E test suite

### `registry-service-task-filtering` Branch

**Purpose**: Advanced task search and filtering
**Base**: `registry-service`
**Additions**: ~3,000 lines

**Features**:

- **Backend**: 4 new REST endpoints for task search
- **Frontend**: TaskExplorer component (1,111 lines)
- **Search**: Filter operators (`=`, `!=`, `>`, `<`, `~`)
- **3-Stage Autocomplete**: Key → Operator → Value
- **DAG Visualization**: Interactive dependency graphs
- **JSONB Queries**: Dynamic parameter filtering

### `registry-service-docs` Branch

**Purpose**: Comprehensive documentation system
**Base**: `registry-service`
**Additions**: ~5,200 lines of documentation

**Structure** (Diátaxis framework):

```
docs/
├── getting-started/    # Quick onboarding
├── concepts/           # Mental models
├── how-to/            # Problem-solving guides
├── configuration/     # Reference docs
├── platform/          # API, UI, self-hosting
└── reference/         # Auto-generated API docs
```

**Tools**: MkDocs + Material theme, mkdocstrings, GitHub Pages

### `cli-workspace-verification` Branch

**Purpose**: Stricter CLI profile validation
**Base**: `registry-service`
**Changes**: ~158 lines (tests) + 25 lines (code)

**Impact**: Changes org/workspace verification from warnings to mandatory errors

---

## Code Quality Assessment

### Tooling

| Tool           | Purpose                  | Configuration           |
| -------------- | ------------------------ | ----------------------- |
| **Ruff**       | Linting + formatting     | Pre-commit hook         |
| **Pyright**    | Static type checking     | Strict mode             |
| **Prettier**   | Markdown/JSON formatting | `--prose-wrap=preserve` |
| **Pytest**     | Testing framework        | `asyncio_mode = "auto"` |
| **Pre-commit** | Git hook management      | 3 hooks configured      |

### Type Safety

- **Full annotations**: All public APIs have type hints
- **Generic types**: `Task[TargetT]`, `AutoTask[LoadedT]`, `Serializer[T]`
- **Protocols**: Protocol-based polymorphism over inheritance
- **Pydantic validation**: Runtime type checking

### Testing

| Area          | Coverage | Notes                                  |
| ------------- | -------- | -------------------------------------- |
| Core Task API | High     | Parametrized tests, namespace handling |
| Targets       | High     | Local, remote, in-memory, directory    |
| Serialization | High     | 9 serializer combinations              |
| Build System  | Medium   | Sequential execution                   |
| Integrations  | Medium   | Prefect async, Modal volumes           |
| Examples      | High     | ML pipeline with sklearn               |

### Code Organization

**Strengths**:

- Clear separation of concerns
- Single responsibility per module
- Consistent naming conventions
- Private APIs prefixed with `_`

**Areas for Improvement**:

- No explicit code coverage metrics
- Dynamic dependency support incomplete
- Parallel execution not implemented

---

## Design Patterns

### 1. Protocol-Based Abstraction

```python
# Minimal interfaces, maximum flexibility
class Target(Protocol):
    def exists(self) -> bool: ...
```

### 2. Provider Pattern

```python
# Dependency injection via resource providers
target_factory_provider = resource_provider(TargetFactory)
target_factory_provider.set(custom_factory)
```

### 3. Factory Pattern

```python
# Target creation routed by URI prefix
prefix_to_target_prototype = {
    "/": LocalTarget,
    "s3://": s3_target_from_path,
    "modalvol://": get_modal_target,
}
```

### 4. Composition over Inheritance

```python
# Tasks compose other tasks as parameters
@task
def aggregate(data: Depends[list[int]], config: Depends[Config]) -> Result:
    ...
```

### 5. Atomic Operations

```python
# All writes are atomic (temp file + rename)
with target.open("w") as f:
    f.write(data)  # Actually writes to .tmp-{uuid}
# Atomic rename on context exit
```

---

## Technology Stack

### Core

| Component   | Technology              |
| ----------- | ----------------------- |
| Language    | Python 3.10+            |
| Type System | Pydantic v2             |
| Build Tool  | uv + Hatch              |
| Testing     | Pytest + pytest-asyncio |

### Registry Service (Feature Branch)

| Component  | Technology                       |
| ---------- | -------------------------------- |
| Backend    | FastAPI + SQLAlchemy + Alembic   |
| Frontend   | React 19 + TypeScript + Tailwind |
| Database   | PostgreSQL with JSONB            |
| Auth       | OIDC (Keycloak/Cognito) + JWT    |
| Deployment | Docker + AWS CDK                 |

### Integrations

| Service  | Purpose                |
| -------- | ---------------------- |
| Prefect  | Workflow orchestration |
| Modal    | Serverless compute     |
| AWS S3   | Cloud storage          |
| Keycloak | Identity provider      |

---

## Summary

### What Makes Stardag Unique

1. **Composability First**: Tasks are first-class composable units, not just functions
2. **Deterministic by Design**: Parameter hashing ensures reproducible builds
3. **Type Safety**: Full Pydantic integration with generics
4. **Storage Abstraction**: Same code works with local/S3/Modal/in-memory
5. **Enterprise Ready**: Multi-tenant registry service with auth

### Maturity Assessment

| Aspect             | Rating     | Notes                              |
| ------------------ | ---------- | ---------------------------------- |
| Core Framework     | ⭐⭐⭐⭐⭐ | Stable, well-tested                |
| Type Safety        | ⭐⭐⭐⭐⭐ | Comprehensive                      |
| Documentation      | ⭐⭐⭐⭐   | Good (excellent with docs branch)  |
| Registry Service   | ⭐⭐⭐⭐   | Production-ready in feature branch |
| Cloud Integrations | ⭐⭐⭐⭐   | Prefect/Modal/S3 working           |
| Parallel Execution | ⭐⭐       | Not implemented                    |

### Recommendations

1. **Merge registry-service**: The feature is mature and adds significant value
2. **Add parallel execution**: Would significantly improve performance
3. **Complete dynamic dependencies**: Currently raises NotImplementedError
4. **Add code coverage**: Would improve confidence in changes
5. **Consider Dagster integration**: Mentioned in README as TODO

---

_This analysis was generated by exploring all source files, tests, examples, and feature branches in the repository._
