# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Institutional-grade repository scaffolding: issue templates, pull request template,
  `CODEOWNERS`, `dependabot.yml`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`.
- Python documentation is now built with [MkDocs](https://www.mkdocs.org/) (Material theme +
  `mkdocstrings`) and published to GitHub Pages, replacing the previous Sphinx/Read the Docs
  setup.
- Dedicated `lint`, `tests`, and `docs` CI workflows with status badges in the README.

### Changed

- Read the Docs is no longer used for Python API documentation; see
  <https://bbalouki.github.io/bbstrader/> instead.

## [2.3.0]

### Added

- `btengine` research and realism stack:
  - `analytics`: historical & parametric VaR/CVaR, Monte Carlo equity-curve confidence bands,
    volatility-regime detection, and factor/beta exposure.
  - `optimize`: parallel parameter sweeps and walk-forward evaluation.
  - `overfitting`: deflated/probabilistic Sharpe ratio, PBO via CSCV, and combinatorial purged
    cross-validation.
  - `friction`: pluggable slippage, market impact, commissions, partial fills, latency, and
    per-bar swap/overnight funding costs.
  - `catalog`: cached, Parquet-backed data catalog (falls back to CSV without `pyarrow`).
  - `vectorized`: vectorized research fast-path (`vectorized_backtest(...)`) for fast
    hypothesis testing across full history.
  - `templates`: ready-made trend / mean-reversion / breakout strategy templates.
  - `timeframe`: on-the-fly higher-timeframe (HTF) resampling.
  - `experiment`: experiment/results store persisting parameters, metrics, and equity curves.
- `core/broker`: venue-neutral `Broker` execution abstraction with an in-memory `PaperBroker`.
- `core/indicators`: built-in vectorized SMA, EMA, RSI, ATR, Bollinger Bands, MACD, and z-score.
- Multi-strategy support over a shared portfolio and multi-timeframe feeds in `btengine`.
- Doxygen-based C++ documentation workflow with automatic GitHub Pages deployment.
- Reproducible benchmark suite for the backtesting engine (`benchmarks/`).

### Changed

- Lean core install: the base `pip install bbstrader` no longer pulls the NLP/social/viz
  stacks by default; install `bbstrader[nlp]`, `bbstrader[social]`, `bbstrader[viz]`, or
  `bbstrader[all]` as needed.

## Earlier releases

See [GitHub Releases](https://github.com/bbalouki/bbstrader/releases) for the full history of
versions prior to 2.3.0.

[Unreleased]: https://github.com/bbalouki/bbstrader/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/bbalouki/bbstrader/releases/tag/v2.3.0
