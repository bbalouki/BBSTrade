import pandas as pd
from bbstrader.btengine.event import (
    OrderEvent, FillEvent, MarketEvent, SignalEvent
)
from queue import Queue
from datetime import datetime
from bbstrader.btengine.data import DataHandler
from bbstrader.btengine.performance import (
    create_drawdowns, plot_performance,
    create_sharpe_ratio, create_sortino_ratio,
    plot_returns_and_dd, plot_monthly_yearly_returns
)


class Portfolio(object):
    """
    This  describes a `Portfolio()` object that keeps track of the positions 
    within a portfolio and generates orders of a fixed quantity of stock based on signals. 
    More sophisticated portfolio objects could include risk management and position 
    sizing tools (such as the `Kelly Criterion`).

    The portfolio order management system is possibly the most complex component of 
    an eventdriven backtester.  Its role is to keep track of all current market positions 
    as well as the market value of the positions (known as the "holdings"). 
    This is simply an estimate of the liquidation value of the position and is derived in part 
    from the data handling facility of the backtester.

    In addition to the positions and holdings management the portfolio must also be aware of 
    risk factors and position sizing techniques in order to optimise orders that are sent 
    to a brokerage or other form of market access.

    Unfortunately, Portfolio and `Order Management Systems (OMS)` can become rather complex!
    So let's keep the `Portfolio` object relatively straightforward  anf improve it foward.

    Continuing in the vein of the Event class hierarchy a Portfolio object must be able 
    to handle `SignalEvent` objects, generate `OrderEvent` objects and interpret `FillEvent` 
    objects to update positions. Thus it is no surprise that the Portfolio objects are often 
    the largest component of event-driven systems, in terms of lines of code (LOC).

    The initialisation of the Portfolio object requires access to the bars `DataHandler`, 
    the  `Event Queue`, a `start datetime stamp` and an `initial capital` 
    value (defaulting to `100,000 USD`) and others parameter based on the `Strategy` requirement.

    The `Portfolio` is designed to handle position sizing and current holdings, 
    but will carry out trading orders in a "dumb" manner by simply sending them directly 
    to the brokerage with a predetermined fixed quantity size, irrespective of cash held. 
    These are all unrealistic assumptions, but they help to outline how a portfolio order 
    management system (OMS) functions in an eventdriven fashion.

    The portfolio contains the `all_positions` and `current_positions` members. 
    The former stores a list of all previous positions recorded at the timestamp of a market data event. 
    A position is simply the quantity of the asset held. Negative positions mean the asset has been shorted.

    The latter current_positions dictionary stores contains the current positions 
    for the last market bar update, for each symbol.

    In addition to the positions data the portfolio stores `holdings`, 
    which describe the current market value of the positions held. "Current market value" 
    in this instance means the closing price obtained from the current market bar, 
    which is clearly an approximation, but is reasonable enough for the time being. 
    `all_holdings` stores the historical list of all symbol holdings, while current_holdings 
    stores the most up to date dictionary of all symbol holdings values.
    """

    def __init__(self,
                 bars: DataHandler,
                 events: Queue,
                 start_date: datetime,
                 initial_capital=100000.0,
                 **kwargs
                 ):
        """
        Initialises the portfolio with bars and an event queue.
        Also includes a starting datetime index and initial capital
        (USD unless otherwise stated).

        Args:
            bars (DataHandler): The DataHandler object with current market data.
            events (Queue): The Event Queue object.
            start_date (datetime): The start date (bar) of the portfolio.
            initial_capital (float): The starting capital in USD.

            kwargs (dict): Additional arguments
                - time_frame: The time frame of the bars.
                - trading_hours: The number of trading hours in a day.
                - benchmark: The benchmark symbol to compare the portfolio.
                - strategy_name: The name of the strategy  (the name must not include 'Strategy' in it).    
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.timeframe = kwargs.get("time_frame", "D1")
        self.trading_hours = kwargs.get("trading_hours", 6.5)
        self.benchmark = kwargs.get('benchmark', 'SPY')
        self.strategy_name = kwargs.get('strategy_name', 'Strategy')

        tf = self._tf_mapping()
        if self.timeframe not in tf:
            raise ValueError(
                f"Timeframe not supported,"
                f"please choose one of the following: "
                f"1m, 3m, 5m, 10m, 15m, 30m, 1h, 2h, 4h, D1"
            )
        else:
            self.tf = tf[self.timeframe]

        self.all_positions = self.construct_all_positions()
        self.current_positions = dict((k, v) for k, v in
                                      [(s, 0) for s in self.symbol_list])
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()

    def _tf_mapping(self):
        """
        Returns a dictionary mapping the time frames
        to the number of bars in a year.
        """
        N = 252
        H = self.trading_hours
        time_frame_mapping = {
            '1m':  N*60*H,
            '3m':  N*(60/3)*H,
            '5m':  N*(60/5)*H,
            '10m': N*(60/10)*H,
            '15m': N*(60/15)*H,
            '30m': N*(60/30)*H,
            '1h':  N*(60/60)*H,
            '2h':  N*(60/120)*H,
            '4h':  N*(60/240)*H,
            'D1':  N
        }
        return time_frame_mapping

    def construct_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        d['Datetime'] = self.start_date
        return [d]

    def construct_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['Datetime'] = self.start_date
        d['Cash'] = self.initial_capital
        d['Commission'] = 0.0
        d['Total'] = self.initial_capital
        return [d]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        d = dict((k, v) for k, v in [(s, 0.0) for s in self.symbol_list])
        d['Cash'] = self.initial_capital
        d['Commission'] = 0.0
        d['Total'] = self.initial_capital
        return d

    def update_timeindex(self, event: MarketEvent):
        """
        Adds a new record to the positions matrix for the current
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).
        Makes use of a MarketEvent from the events queue.
        """
        latest_datetime = self.bars.get_latest_bar_datetime(
            self.symbol_list[0]
        )
        # Update positions
        # ================
        dp = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dp['Datetime'] = latest_datetime
        for s in self.symbol_list:
            dp[s] = self.current_positions[s]
        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        # ===============
        dh = dict((k, v) for k, v in [(s, 0) for s in self.symbol_list])
        dh['Datetime'] = latest_datetime
        dh['Cash'] = self.current_holdings['Cash']
        dh['Commission'] = self.current_holdings['Commission']
        dh['Total'] = self.current_holdings['Cash']
        for s in self.symbol_list:
            # Approximation to the real value
            market_value = self.current_positions[s] * \
                self.bars.get_latest_bar_value(s, "Adj Close")
            dh[s] = market_value
            dh['Total'] += market_value

        # Append the current holdings
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill: FillEvent):
        """
        Takes a Fill object and updates the position matrix to
        reflect the new position.

        Args:
            fill (FillEvent): The Fill object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        self.current_positions[fill.symbol] += fill_dir*fill.quantity

    def update_holdings_from_fill(self, fill: FillEvent):
        """
        Takes a Fill object and updates the holdings matrix to
        reflect the holdings value.

        Args:
            fill (FillEvent): The Fill object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = self.bars.get_latest_bar_value(
            fill.symbol, "Adj Close"
        )
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['Commission'] += fill.commission
        self.current_holdings['Cash'] -= (cost + fill.commission)
        self.current_holdings['Total'] -= (cost + fill.commission)

    def update_fill(self, event: FillEvent):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        if event.type == 'FILL':
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal: SignalEvent):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Args:
            signal (SignalEvent): The tuple containing Signal information.
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        quantity = signal.quantity
        strength = signal.strength
        cur_quantity = self.current_positions[symbol]

        order_type = 'MKT'
        mkt_quantity = round(quantity * strength)

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')

        return order

    def update_signal(self, event: SignalEvent):
        """
        Acts on a SignalEvent to generate new orders
        based on the portfolio logic.
        """
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('Datetime', inplace=True)
        curve['Returns'] = curve['Total'].pct_change(fill_method=None)
        curve['Equity Curve'] = (1.0+curve['Returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        total_return = self.equity_curve['Equity Curve'].iloc[-1]
        returns = self.equity_curve['Returns']
        pnl = self.equity_curve['Equity Curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=self.tf)
        sortino_ratio = create_sortino_ratio(returns, periods=self.tf)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['Drawdown'] = drawdown

        stats = [
            ("Total Return", f"{(total_return-1.0) * 100.0:.2f}%"),
            ("Sharpe Ratio", f"{sharpe_ratio:.2f}"),
            ("Sortino Ratio", f"{sortino_ratio:.2f}"),
            ("Max Drawdown", f"{max_dd * 100.0:.2f}%"),
            ("Drawdown Duration", f"{dd_duration}")
        ]
        self.equity_curve.to_csv('equity.csv')
        plot_performance(self.equity_curve, self.strategy_name)
        plot_returns_and_dd(self.equity_curve,
                            self.benchmark, self.strategy_name)
        plot_monthly_yearly_returns(self.equity_curve, self.strategy_name)

        return stats
