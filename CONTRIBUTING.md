# Contributing to bbstrader

Thanks for your interest in contributing! `bbstrader` is a hybrid C++/Python project, so
contributions can range from pure-Python quant models to native C++ bridge code. This guide
covers how to get set up and how to submit changes.

By participating in this project you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## Table of Contents

- [Ways to contribute](#ways-to-contribute)
- [Project layout](#project-layout)
- [Development setup](#development-setup)
  - [Python](#python)
  - [C++](#c)
- [Running the test suite](#running-the-test-suite)
- [Linting and formatting](#linting-and-formatting)
- [Documentation](#documentation)
- [Commit messages and pull requests](#commit-messages-and-pull-requests)
- [Versioning](#versioning)
- [Reporting bugs and requesting features](#reporting-bugs-and-requesting-features)
- [Security issues](#security-issues)

## Ways to contribute

- Report bugs or propose features via [GitHub Issues](https://github.com/bbalouki/bbstrader/issues/new/choose).
- Improve documentation (guides, docstrings, examples).
- Fix bugs or implement features from the issue tracker (look for `good first issue` / `help wanted`).
- Add or improve tests, especially around edge cases in `btengine`, `metatrader`, and `models`.

For anything non-trivial (new modules, breaking API changes, new dependencies), please open an
issue first to discuss the approach before investing time in an implementation.

## Project layout

```
src/bbstrader/    Python package (btengine, metatrader, trading, models, core, api, config)
include/          C++ public headers
src/cpp/          C++ implementation and pybind11 bindings
tests/            Python tests (pytest) and C++ tests (tests/cpp, run via CTest)
docs/             mkdocs documentation sources
examples/         Example strategies and scripts
benchmarks/       Performance benchmarks for the backtesting engine
```

## Development setup

### Python

`bbstrader` targets Python 3.12+. We use [uv](https://docs.astral.sh/uv/) for dependency
management, but plain `pip` works too.

```bash
git clone https://github.com/bbalouki/bbstrader.git
cd bbstrader

# Using uv (recommended) - add --extra mt5 on Windows, since several tests
# import the MetaTrader5 package unconditionally.
uv sync --group dev --group docs --extra all
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# ...or with pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"          # add ".[all,mt5]" on Windows
pip install pytest pytest-mock ruff mypy mkdocs-material "mkdocstrings[python]"
```

The Python package wraps a compiled C++ extension (`bbstrader.api.client`). `pip install -e .`
(via `scikit-build-core`) compiles it for you; see [C++](#c) below for the toolchain
prerequisites.

### C++

The C++ core uses CMake (>= 3.20) and [vcpkg](https://github.com/microsoft/vcpkg) for
dependencies.

```bash
git clone https://github.com/microsoft/vcpkg
./vcpkg/bootstrap-vcpkg.sh   # or bootstrap-vcpkg.bat on Windows

cmake -S . -B build \
  -DBBSTRADER_BUILD_TESTS=ON \
  -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake

cmake --build build
ctest --test-dir build --output-on-failure
```

A ready-made `win` CMake preset (MSVC + vcpkg) is available in `CMakePresets.json` for Windows
development in Visual Studio / VS Code.

## Running the test suite

Python:

```bash
pytest tests -k "not test_metatrader_client"
```

`test_metatrader_client` requires a live MetaTrader 5 terminal and Windows, so it's excluded from
the default run; CI covers it separately where applicable.

C++ (from the CMake build directory configured with `BBSTRADER_BUILD_TESTS=ON`):

```bash
ctest --test-dir build --output-on-failure
```

Please add tests for any new behavior or bug fix. Follow the existing structure under
`tests/<module>/` for Python and `tests/cpp/` for C++.

## Linting and formatting

Python:

```bash
ruff format .
ruff check .
mypy   # advisory: see note below
```

`mypy` runs in CI as an informational (non-blocking) step while the codebase's type coverage is
being improved incrementally; please still try not to introduce new, obviously-wrong type errors
in code you touch.

C++:

```bash
clang-format -i <changed files>
```

`clang-format` and `clang-tidy` are already wired into the CMake build via
`BBSTRADER_APPLY_FORMATING` / `BBSTRADER_APPLY_CLANG_TIDY_GLOBALY` (see `CMakePresets.json`).
Please follow the style already established in `include/` and `src/cpp/` (RAII, smart pointers,
`const`-correctness, no raw owning pointers, etc.). CI runs a `clang-format --dry-run` check as an
advisory (non-blocking) step while the existing sources catch up to the pinned formatter version.

Consider installing the pre-commit hooks so these checks run automatically:

```bash
pip install pre-commit
pre-commit install
```

## Documentation

Documentation is built with [MkDocs](https://www.mkdocs.org/) (Material theme) from `docs/` and
published to [GitHub Pages](https://bbalouki.github.io/bbstrader/). API reference pages are
generated from docstrings via `mkdocstrings`, so keeping docstrings accurate is the main way to
keep the reference docs up to date.

To preview the docs locally:

```bash
uv sync --group docs
mkdocs serve
```

C++ API docs are generated separately with Doxygen from `include/bbstrader` and published
alongside the Python docs.

## Commit messages and pull requests

- Keep commits focused; prefer several small, reviewable commits over one large one.
- Write commit messages that explain *why* a change was made, not just what changed.
- Fill out the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) completely.
- Add an entry to [CHANGELOG.md](CHANGELOG.md) under `Unreleased` for user-facing changes.
- Ensure `ruff format`, `ruff check`, and the test suite pass before requesting review; CI will
  also run these checks automatically.
- A pull request should generally target the `main` branch.

## Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/). A breaking change is any
backward-incompatible modification to the public API, including data schemas, the CLI, and the
C++/Python binding surface. Please flag breaking changes clearly in your PR description.

## Reporting bugs and requesting features

Please use the issue templates:

- [🐛 Bug Report](https://github.com/bbalouki/bbstrader/issues/new?template=bug_report.yml)
- [🚀 Feature Request](https://github.com/bbalouki/bbstrader/issues/new?template=feature_request.yml)
- [📚 Documentation](https://github.com/bbalouki/bbstrader/issues/new?template=documentation.yml)

## Security issues

Please do **not** open public issues for security vulnerabilities. See
[SECURITY.md](SECURITY.md) for how to report them responsibly.
