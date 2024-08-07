import os.path
import numpy as np
import pandas as pd
from bbstrader.btengine.event import MarketEvent
from queue import Queue
from abc import ABCMeta, abstractmethod


class DataHandler(metaclass=ABCMeta):
    """
    One of the goals of an event-driven trading system is to minimise 
    duplication of code between the backtesting element and the live execution 
    element. Ideally it would be optimal to utilise the same signal generation 
    methodology and portfolio management components for both historical testing 
    and live trading. In order for this to work the Strategy object which generates
    the Signals, and the `Portfolio` object which provides Orders based on them, 
    must utilise an identical interface to a market feed for both historic and live 
    running.

    This motivates the concept of a class hierarchy based on a `DataHandler` object,
    which givesall subclasses an interface for providing market data to the remaining 
    components within thesystem. In this way any subclass data handler can be "swapped out", 
    without affecting strategy or portfolio calculation.

    Specific example subclasses could include `HistoricCSVDataHandler`, 
    `EODHDDataHandler`, `FMPDataHandler`, `IBMarketFeedDataHandler` etc.
    """

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError(
            "Should implement get_latest_bar()"
        )

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError(
            "Should implement get_latest_bars()"
        )

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError(
            "Should implement get_latest_bar_datetime()"
        )

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Adj Close, Volume or Returns
        from the last bar.
        """
        raise NotImplementedError(
            "Should implement get_latest_bar_value()"
        )

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError(
            "Should implement get_latest_bars_values()"
        )

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, Open, High, Low,
        Close, Adj Close, Volume, Retruns).
        """
        raise NotImplementedError(
            "Should implement update_bars()"
        )


class HistoricCSVDataHandler(DataHandler):
    """
    `HistoricCSVDataHandler` is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.
    """

    def __init__(self,
                 events: Queue,
                 csv_dir: str,
                 symbol_list: list[str]
                 ):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.
        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Args:
            events (Queue): The Event Queue.
            csv_dir (str): Absolute directory path to the CSV files.
            symbol_list (list[str]): A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens the CSV files from the data directory, converting
        them into pandas DataFrames within a symbol dictionary.
        """
        comb_index = None
        for s in self.symbol_list:
            # Load the CSV file with no header information,
            # indexed on date
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, f'{s}.csv'),
                header=0, index_col=0, parse_dates=True,
                names=[
                    'Datetime', 'Open', 'High',
                    'Low', 'Close', 'Adj Close', 'Volume'
                ]
            )
            self.symbol_data[s].sort_index(inplace=True)

            # Combine the index to pad forward values
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)

            # Set the latest symbol_data to None
            self.latest_symbol_data[s] = []

        # Reindex the dataframes
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index, method='pad'
            )
            self.symbol_data[s]["Returns"] = self.symbol_data[s][
                "Adj Close"
            ].pct_change().dropna()
            self.symbol_data[s] = self.symbol_data[s].iterrows()

    def _get_new_bar(self, symbol: str):
        """
        Returns the latest bar from the data feed.
        """
        for b in self.symbol_data[symbol]:
            yield b

    def get_latest_bar(self, symbol: str):
        """
        Returns the last bar from the latest_symbol list.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Symbol not available in the historical data set.")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol: str, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Symbol not available in the historical data set.")
            raise
        else:
            return bars_list[-N:]

    def get_latest_bar_datetime(self, symbol: str):
        """
        Returns a Python datetime object for the last bar.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Symbol not available in the historical data set.")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol: str, val_type: str):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Symbol not available in the historical data set.")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)

    def get_latest_bars_values(self, symbol: str, val_type: str, N=1):
        """
        Returns the last N bar values from the
        latest_symbol list, or N-k if less available.
        """
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("That symbol is not available in the historical data set.")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])

    def update_bars(self):
        """
        Pushes the latest bar to the latest_symbol_data structure
        for all symbols in the symbol list.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())

# TODO # Get data from FinancialModelingPrep ()
class FMPDataHandler(DataHandler):...

# TODO
class MT5DataHandler(DataHandler):...