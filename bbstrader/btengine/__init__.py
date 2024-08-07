"""
# Event-Driven Backtesting Engine

## Overview

This Backtesting Module provides a comprehensive suite of tools to test trading strategies in an event-driven system. 
It simulates the execution of trades in historical market conditions to evaluate the performance of trading strategies 
before applying them in live trading environments. Designed with modularity and extensibility in mind, it caters to 
both novices and experts in algorithmic trading.

## Features

- **Event-Driven Architecture**: Processes market data, generates signals, executes orders, and manages portfolio updates 
in response to events, closely mimicking live trading environments.
- **Historical Market Data Support**: Utilizes historical OHLCV data from CSV files, allowing for the testing of 
strategies over various market conditions and time frames.
- **Strategy Implementation Flexibility**: Abstract base classes for strategies and other components enable users to 
define custom trading logic and data handling processes.
- **Performance Metrics Calculation**: Includes tools for calculating key performance indicators, such as Sharpe Ratio, 
Sortino Ratio, and drawdowns, to evaluate the effectiveness of trading strategies.
- **Visualization**: Generates plots of the equity curve, returns, drawdowns, and other metrics for comprehensive 
strategy performance analysis.

## Components

- **Backtest**: Orchestrates the backtesting process, managing events and invoking components.
- **Event**: Abstract class for events, with implementations for market data, signals, fill and order events.
- **DataHandler**: Abstract class for market data handling, with an implementation for historical CSV data. We will add 
another data handling in the future such as MacroEconomic Data, Fundamental Data, TICK Data and Real-time Data.
- **Strategy**: Abstract class for trading strategies, allowing for custom signal generation logic.
- **Portfolio**: Manages positions and calculates performance metrics, responding to market data and signals.
- **ExecutionHandler**: Abstract class for order execution, with a simulated execution handler provided.
- **Performance**: Utility functions for calculating performance metrics and visualizing strategy performance.

## Usage
```python
from bbstrader.btengine import (
    Backtest, HistoricCSVDataHandler,
    SimulatedExecutionHandler, Portfolio
)
from your_strategy import YourStrategy

if __name__ == "__main__":
    csv_dir = "path_to_your_csv_data_directory"
    symbol_list = ["AAPL", "GOOG"]
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = "2020-01-01"
    
    kwargs = {
        "time_frame": '1h',
        "benchmarck": 'SPY
    }
    backtest = Backtest(
        csv_dir,
        symbol_list,
        initial_capital,
        heartbeat,
        start_date,
        HistoricCSVDataHandler,
        SimulatedExecutionHandler,
        Portfolio,
        YourStrategy,
        **kwargs
    )

    backtest.simulate_trading()
```
"""
from bbstrader.btengine.data import *
from bbstrader.btengine.event import *
from bbstrader.btengine.backtest import *
from bbstrader.btengine.execution import *
from bbstrader.btengine.performance import *
from bbstrader.btengine.portfolio import *
from bbstrader.btengine.strategy import *