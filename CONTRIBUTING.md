# Contributing to python-service-template

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Git Flow Branching Strategy](#git-flow-branching-strategy)
- [Branch Types](#branch-types)
- [Workflow Guidelines](#workflow-guidelines)
- [Development Setup](#development-setup)
- [Code Quality](#code-quality)
- [Pull Request Process](#pull-request-process)

---

## Git Flow Branching Strategy

This project follows the [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) branching model to ensure a consistent and organized development workflow.

### Branch Overview

```
main ─────────────────────────────────────────────────────►
         │                    ▲                    ▲
         │                    │                    │
         ▼                    │                    │
develop ──────────────────────┼────────────────────┼──────►
    │         ▲         │     │         ▲         │
    │         │         │     │         │         │
    ▼         │         ▼     │         │         ▼
feature/*     │     release/* │     hotfix/*   feature/*
              │               │         │
              └───────────────┴─────────┘
```

---

## Branch Types

### `main`
- **Purpose:** Production-ready code only
- **Protection:** Direct commits are not allowed; changes come through `release/*` or `hotfix/*` branches
- **Tagging:** Each merge to `main` should be tagged with a version number (e.g., `v1.0.0`)

### `develop`
- **Purpose:** Integration branch for features; contains the latest development changes
- **Protection:** Direct commits are discouraged; changes come through `feature/*` branches
- **Base for:** All `feature/*` branches

### `feature/*`
- **Purpose:** Development of new features or enhancements
- **Naming:** `feature/<issue-number>-<short-description>` (e.g., `feature/123-add-user-auth`)
- **Base:** Created from `develop`
- **Merge to:** `develop` via pull request

### `release/*`
- **Purpose:** Preparation for a new production release
- **Naming:** `release/<version>` (e.g., `release/1.2.0`)
- **Base:** Created from `develop`
- **Merge to:** Both `main` and `develop` when complete
- **Activities:** Bug fixes, documentation updates, version bumps

### `hotfix/*`
- **Purpose:** Critical fixes for production issues
- **Naming:** `hotfix/<issue-number>-<short-description>` (e.g., `hotfix/456-fix-auth-bug`)
- **Base:** Created from `main`
- **Merge to:** Both `main` and `develop` when complete

---

## Workflow Guidelines

### Starting a New Feature

1. Ensure your local `develop` branch is up to date:
   ```sh
   git checkout develop
   git pull origin develop
   ```

2. Create a new feature branch:
   ```sh
   git checkout -b feature/<issue-number>-<short-description>
   ```

3. Make your changes and commit regularly:
   ```sh
   git add .
   git commit -m "feat: description of changes"
   ```

4. Push your branch and create a pull request to `develop`:
   ```sh
   git push origin feature/<issue-number>-<short-description>
   ```

### Creating a Release

1. Create a release branch from `develop`:
   ```sh
   git checkout develop
   git pull origin develop
   git checkout -b release/<version>
   ```

2. Make release-specific changes (version bumps, changelog updates)

3. Create pull requests to both `main` and `develop`

4. After merging to `main`, tag the release:
   ```sh
   git checkout main
   git pull origin main
   git tag -a v<version> -m "Release v<version>"
   git push origin v<version>
   ```

### Creating a Hotfix

1. Create a hotfix branch from `main`:
   ```sh
   git checkout main
   git pull origin main
   git checkout -b hotfix/<issue-number>-<short-description>
   ```

2. Fix the issue and commit:
   ```sh
   git add .
   git commit -m "fix: description of fix"
   ```

3. Create pull requests to both `main` and `develop`

---

## Development Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ntphiep/fastapi-uv-servive-template.git
   cd fastapi-uv-servive-template
   ```

2. **Install dependencies:**
   ```sh
   uv sync
   ```

3. **Copy environment config:**
   ```sh
   cp .env.default .env
   ```

4. **Install pre-commit hooks:**
   ```sh
   uvx pre-commit install
   ```

5. **Run the application:**
   ```sh
   python src/python_service_template/app.py --reload
   ```

---

## Code Quality

Before submitting a pull request, ensure your code passes all quality checks:

| Check | Command |
|-------|---------|
| Lint | `ruff check --fix` |
| Format | `ruff format` |
| Type check | `mypy src/ tests/` |
| Tests | `pytest` |
| All pre-commit hooks | `uvx pre-commit run --all-files` |

---

## Pull Request Process

1. **Ensure your branch is up to date** with the target branch (`develop` for features, `main` for hotfixes)

2. **Run all quality checks** before submitting

3. **Create a pull request** with:
   - A clear title describing the change
   - A description of what was changed and why
   - Reference to any related issues (e.g., "Closes #123")

4. **Address review feedback** promptly

5. **Squash commits** if requested by maintainers

6. **Wait for CI checks** to pass before requesting a merge

---

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add user authentication endpoint
fix: resolve memory leak in coffee client
docs: update API documentation
```

---

## Questions?

If you have questions about contributing, please open an issue or reach out to the maintainers.
