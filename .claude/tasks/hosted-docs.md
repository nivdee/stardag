# User Friendly Hosted Documentation

## Status

**in-progress** - Initial implementation complete, ready for review and launch

## Goal

Get up user friendly documentation of the entire Stardag "offering" (incl. SDK, API, UI) on `https://docs.stardag.com`.

## Instructions

Implement host documentation based on MkDocs + Material for MkDocs (+ mkdocstrings) and other best practices for this purpose.

Guidelines:

- Take inspiration from [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/latest/), and [Prefect](https://docs.prefect.io/v3/get-started).
- Implement best solution for hosting (on most likely AWS?)
- Initialize the docs based on your understanding of this repo inclduiong existing README:s and USER GUIDES etc.
- Make it well structured and user friendly with gradual learning curve (sections like "Core Concepts", "Quick Start", "Advanced" etc.) do your best at filling with content, but keep it concise and add _clear TODOs_ where content is missing or you need my verification of the interpretation the system/offering.

## Context

See repo and previous tasks.

## Execution Plan

### Summary Of Preparatory Analysis

**Existing Documentation:**

- `/README.md` - Main overview with hello world example, Luigi comparison
- `/USER_GUIDE.md` - Partially completed guide (many TODOs)
- `/CONFIGURATION_GUIDE.md` - Comprehensive config/auth/CLI guide
- `/DEV_README.md` - Development setup
- `/app/README.md` - Quick start for API/UI
- `/lib/stardag-examples/*/README.md` - Example-specific guides

**Key SDK Concepts to Document:**

- Three levels of task API (@task decorator, AutoTask, base Task)
- Parameter hashing and deterministic paths
- Target abstraction (local, S3, in-memory)
- Target roots and environment switching
- Build/execution models (sequential, API registry)
- Dependency injection (Depends, TaskLoads, TaskSet)

**Existing AWS Infrastructure:**

- CDK project in `infra/aws-cdk/` with S3 + CloudFront pattern
- Same pattern can be reused for `docs.stardag.com`
- Route 53 hosted zone already configured for `stardag.com`

### Plan

#### Phase 1: Project Setup

1.1 Create docs directory structure:

```
docs/
├── mkdocs.yml              # MkDocs configuration
├── pyproject.toml          # Python dependencies (mkdocs, material, mkdocstrings)
├── docs/
│   ├── index.md            # Landing page
│   ├── assets/             # Images, logos
│   └── ...                 # Content organized by section
└── overrides/              # Material theme customizations
```

1.2 Configure MkDocs with Material theme:

- Navigation structure
- Search configuration
- Code highlighting
- Dark/light mode toggle
- Social cards (optional)

  1.3 Configure mkdocstrings:

- Link to `lib/stardag/src/stardag/`
- Auto-generate API reference from docstrings

#### Phase 2: Documentation Structure

Based on analysis of reference docs (FastAPI, Pydantic, Prefect):

```
docs/
├── index.md                      # Landing page with value prop
├── getting-started/
│   ├── index.md                  # Overview
│   ├── installation.md           # pip install, prerequisites
│   ├── quickstart.md             # Hello world example
│   └── first-dag.md              # Build your first DAG
├── concepts/
│   ├── index.md                  # Core concepts overview
│   ├── tasks.md                  # What is a task?
│   ├── dependencies.md           # Task dependencies (Depends)
│   ├── parameter-hashing.md      # Deterministic IDs
│   ├── targets.md                # Target abstraction
│   └── build-execution.md        # How builds work
├── tutorials/
│   ├── index.md
│   ├── ml-pipeline.md            # Complete ML example
│   └── data-processing.md        # ETL-style example
├── how-to/
│   ├── index.md
│   ├── define-tasks.md           # Three levels of API
│   ├── configure-storage.md      # Target roots, S3
│   ├── use-api-registry.md       # Distributed builds
│   ├── integrate-prefect.md      # Prefect orchestration
│   └── integrate-modal.md        # Modal serverless
├── configuration/
│   ├── index.md
│   ├── profiles.md               # Environment switching
│   ├── workspaces.md             # Org/workspace structure
│   └── cli.md                    # CLI commands
├── platform/
│   ├── index.md                  # API & UI overview
│   ├── api.md                    # API service
│   ├── ui.md                     # Web dashboard
│   └── self-hosting.md           # Deployment guide
├── reference/
│   ├── index.md
│   ├── api/                      # Auto-generated from mkdocstrings
│   └── exceptions.md             # Error types
└── changelog.md
```

#### Phase 3: Content Creation

3.1 **Core Content (from existing docs):**

- Migrate and polish content from README.md, USER_GUIDE.md, CONFIGURATION_GUIDE.md
- Ensure consistency and fill gaps

  3.2 **New Content:**

- Add missing conceptual explanations (parameter hashing, build semantics)
- Create step-by-step tutorials
- Document Platform (API/UI) features

  3.3 **API Reference:**

- Ensure docstrings in SDK code are comprehensive
- Configure mkdocstrings for auto-generation

  3.4 **TODOs for Verification:**

- Mark unclear sections with `<!-- TODO: Verify with maintainer -->`
- List areas needing content/examples

#### Phase 4: AWS Hosting

4.1 Add CDK stack for docs (`DocsStack`):

- S3 bucket for static docs
- CloudFront distribution
- DNS record for `docs.stardag.com`
- ACM certificate (in FoundationStack)

  4.2 Create deployment script:

- Build docs with `mkdocs build`
- Sync to S3
- Invalidate CloudFront cache

  4.3 (Optional) GitHub Actions for CI/CD:

- Auto-deploy on push to main
- Preview deploys for PRs

#### Phase 5: Polish & Launch

5.1 Final review:

- Check all links
- Test search functionality
- Verify mobile responsiveness

  5.2 SEO basics:

- Meta descriptions
- Sitemap generation
- robots.txt

## Decisions

| Decision          | Choice                            | Rationale                                                    |
| ----------------- | --------------------------------- | ------------------------------------------------------------ |
| Docs framework    | MkDocs + Material                 | Python ecosystem, great DX, used by FastAPI/Pydantic/Prefect |
| API reference     | mkdocstrings                      | Auto-generates from docstrings, stays in sync                |
| Hosting           | **GitHub Pages**                  | Simplest option, no CDK changes needed                       |
| Docs location     | `/docs` at repo root              | Standard location, easy CI/CD                                |
| Content structure | Diátaxis-inspired                 | Tutorials/How-to/Reference/Explanation separation            |
| CI/CD             | GitHub Actions (TODO - follow-up) | Auto-deploy on push to main                                  |
| Content scope     | SDK + CLI + API + UI basics       | Full offering documented, minimal but complete               |
| Branding          | Centralized config                | Extract from UI, make easy to update later                   |
| Analytics         | Prepared, not implemented         | Add Google Analytics/Plausible hooks, enable later           |
| Docstrings        | Add placeholders with TODOs       | Will be cleaned up by maintainer                             |

### Branding (from UI analysis)

**Color Palette:**

- Primary: Blue-600 (`#2563eb`) / Blue-700 (`#1d4ed8`)
- Backgrounds: White, Gray-50, Gray-100
- Text: Gray-900, Gray-700, Gray-600
- Borders: Gray-200, Gray-300
- Dark mode: Gray-800/900 backgrounds, Gray-100/200 text

**Status Colors:**

- Pending: Yellow
- Running: Blue
- Completed: Green
- Failed: Red

**Typography:** System fonts (system-ui, Avenir, Helvetica, Arial, sans-serif)

## Progress

- [x] Analyze existing documentation
- [x] Research reference implementations (FastAPI, Pydantic, Prefect)
- [x] Review AWS infrastructure
- [x] Create execution plan
- [x] Phase 1: Project setup
  - [x] `docs/pyproject.toml` with uv-managed dependencies
  - [x] `docs/mkdocs.yml` with Material theme + mkdocstrings
  - [x] Branding colors extracted from UI
- [x] Phase 2: Documentation structure
  - [x] Navigation structure in mkdocs.yml
  - [x] All section directories and index pages
- [x] Phase 3: Content creation
  - [x] Getting Started (4 pages): index, installation, quickstart, first-dag
  - [x] Concepts (6 pages): index, tasks, dependencies, parameter-hashing, targets, build-execution
  - [x] How-To (6 pages): index, define-tasks, configure-storage, use-api-registry, integrate-prefect, integrate-modal
  - [x] Configuration (4 pages): index, profiles, workspaces, cli
  - [x] Platform (4 pages): index, api, ui, self-hosting
  - [x] Reference (3 pages): index, api, exceptions
  - [x] Module docstring added to `stardag/__init__.py`
- [x] Phase 4: Hosting setup
  - [x] `.github/workflows/docs.yml` for GitHub Pages
  - [x] `docs/README.md` with development instructions
- [ ] Phase 5: Launch (remaining)

## Remaining TODOs

### High Priority (for launch)

- [ ] **Enable GitHub Pages**: In repo Settings > Pages, set source to "GitHub Actions"
- [ ] **Review content**: Verify accuracy of SDK/CLI/API documentation
- [ ] **Test locally**: Run `uv run mkdocs serve` and check all pages render correctly

### Medium Priority (post-launch)

- [ ] **Enable auto-deploy**: Uncomment `on: push` trigger in `.github/workflows/docs.yml`
- [ ] **Custom domain**: Configure `docs.stardag.com` DNS (CNAME to GitHub Pages)
- [ ] **Fix docstring warnings**: Clean up `target/_factory.py` docstrings for strict mode
- [ ] **Add logo**: Create/add Stardag logo to `docs/docs/assets/` and update mkdocs.yml

### Low Priority (enhancements)

- [ ] **Enable analytics**: Uncomment analytics section in mkdocs.yml
- [ ] **Add tutorials section**: ML pipeline tutorial, data processing tutorial
- [ ] **Expand API reference**: Add more comprehensive docstrings to SDK
- [ ] **Add changelog**: Create docs/docs/changelog.md
- [ ] **Social cards**: Enable Material social cards plugin for link previews

### Content TODOs (marked in docs)

The following pages contain `<!-- TODO -->` comments needing verification:

- `concepts/tasks.md` - Versioning behavior, auto_namespace
- `concepts/dependencies.md` - TaskSet behavior
- `concepts/parameter-hashing.md` - IDHashInclude syntax, IDHasher
- `concepts/targets.md` - Custom serializer implementation
- `concepts/build-execution.md` - Error handling, retry logic, parallelization
- `how-to/define-tasks.md` - More examples and patterns
- `how-to/integrate-modal.md` - modal_task decorator syntax
- `platform/api.md` - Complete API reference, rate limits
- `platform/ui.md` - Screenshots
- `platform/self-hosting.md` - Unauthenticated mode

## Files Created/Modified

```
docs/
├── README.md                    # Development guide (NEW)
├── pyproject.toml               # Dependencies (NEW)
├── mkdocs.yml                   # Configuration (NEW)
└── docs/                        # 27 markdown files (NEW)
    ├── index.md
    ├── getting-started/         # 4 files
    ├── concepts/                # 6 files
    ├── how-to/                  # 6 files
    ├── configuration/           # 4 files
    ├── platform/                # 4 files
    └── reference/               # 3 files

.github/workflows/docs.yml       # CI/CD workflow (NEW)
lib/stardag/src/stardag/__init__.py  # Added module docstring (MODIFIED)
```

## Notes

### Development Commands

```bash
cd docs
uv sync                    # Install dependencies
uv run mkdocs serve        # Preview at localhost:8000
uv run mkdocs build        # Build to docs/site/
```

### Reference Examples

- [FastAPI Docs](https://fastapi.tiangolo.com/) - Excellent structure, code examples
- [Pydantic Docs](https://docs.pydantic.dev/) - Clean API reference integration
- [Prefect Docs](https://docs.prefect.io/) - Good getting started flow
