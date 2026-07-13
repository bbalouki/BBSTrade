# API Reference

This section is generated automatically from docstrings in `src/bbstrader` via
[mkdocstrings](https://mkdocstrings.github.io/). It mirrors the package layout:

| Package                        | Purpose                                                            |
| ------------------------------- | -------------------------------------------------------------------- |
| [`bbstrader.api`](api.md)         | Handler injections for the C++/Python bridge (`Mt5Handlers`, etc.). |
| [`bbstrader.btengine`](btengine.md) | Event-driven backtesting engine, research, and realism toolkit.    |
| [`bbstrader.core`](core.md)       | Shared utilities: broker abstraction, data structures, indicators. |
| [`bbstrader.metatrader`](metatrader.md) | MetaTrader 5 account, trading, risk, and copy-trading APIs.   |
| [`bbstrader.models`](models.md)   | Quant/NLP models: sentiment analysis, portfolio optimization.      |
| [`bbstrader.trading`](trading.md) | Live execution and strategy orchestration.                        |
| [Config & CLI](misc.md)          | `bbstrader.config` and the `python -m bbstrader` entry point.      |

!!! note "Compiled C++ bindings"
    `bbstrader.api.client` is a compiled pybind11 extension (no Python source), so it cannot be
    introspected by the documentation generator here. Its API is documented from the C++ headers
    instead — see the [C++ API docs](/bbstrader/cpp/).
