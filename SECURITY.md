# Security Policy

## Supported Versions

`bbstrader` follows [Semantic Versioning](https://semver.org/). Security fixes are made against
the latest minor release on the current major version. Older major versions are not maintained.

| Version | Supported          |
| ------- | ------------------ |
| 2.x     | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report it privately using one of:

1. **GitHub Private Vulnerability Reporting** (preferred): open a
   [new security advisory](https://github.com/bbalouki/bbstrader/security/advisories/new) for
   this repository.
2. **Email**: [bertin@bbs-trading.com](mailto:bertin@bbs-trading.com) with details of the issue.

Please include, where possible:

- A description of the vulnerability and its potential impact.
- Steps to reproduce, or a minimal proof-of-concept.
- The affected version(s) and component(s) (Python package, C++ core, CLI, or copy-trading GUI).

### What to expect

- Acknowledgement of your report within **5 business days**.
- An initial assessment of severity and impact within **10 business days**.
- We will keep you informed as a fix is developed, and credit you in the release notes /
  advisory unless you prefer to remain anonymous.
- Once a fix is released, we will publish a GitHub Security Advisory describing the issue and
  affected versions.

We ask that you give us a reasonable amount of time to address the issue before any public
disclosure.

## Scope

`bbstrader` connects to live trading infrastructure (MetaTrader 5) and handles account
credentials, API keys, and order execution. Issues in scope include, but are not limited to:

- Remote code execution, memory-safety bugs, or crashes in the C++ core or Python bindings.
- Credential or secret leakage (e.g. broker logins, API tokens, `.env` values) via logs, error
  messages, or the copy-trading GUI.
- Command/argument injection in the CLI or configuration loading.
- Insecure handling of network communication with brokers or data providers.

Issues in strategy logic itself (e.g. a backtest producing an unprofitable strategy) are not
security vulnerabilities.

## Third-Party Dependencies

Dependency updates (including security patches) are tracked via
[Dependabot](.github/dependabot.yml). If you discover a vulnerability in a dependency that
affects `bbstrader`, please still report it using the process above so we can assess impact and
issue an update.
