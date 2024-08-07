import datetime
from bbstrader.btengine.event import FillEvent, OrderEvent
from queue import Queue
from abc import ABCMeta, abstractmethod


class ExecutionHandler(metaclass=ABCMeta):
    """
    The ExecutionHandler abstract class handles the interaction
    between a set of order objects generated by a Portfolio and
    the ultimate set of Fill objects that actually occur in the
    market.

    The handlers can be used to subclass simulated brokerages
    or live brokerages, with identical interfaces. This allows
    strategies to be backtested in a very similar manner to the
    live trading engine.

    The ExecutionHandler described here is exceedingly simple, 
    since it fills all orders at the current market price. 
    This is highly unrealistic, but serves as a good baseline for improvement.
    """

    @abstractmethod
    def execute_order(self, event: OrderEvent):
        """
        Takes an Order event and executes it, producing
        a Fill event that gets placed onto the Events queue.

        Args:
            event (OrderEvent): Contains an Event object with order information.
        """
        raise NotImplementedError(
            "Should implement execute_order()"
        )


class SimulatedExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, events: Queue):
        """
        Initialises the handler, setting the event queues
        up internally.

        Args:
            events (Queue): The Queue of Event objects.
        """
        self.events = events

    def execute_order(self, event: OrderEvent):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Args:
            event (OrderEvent): Contains an Event object with order information.
        """
        if event.type == 'ORDER':
            fill_event = FillEvent(
                datetime.datetime.now(), event.symbol,
                'ARCA', event.quantity, event.direction, None
            )
            self.events.put(fill_event)

# TODO # Use in live execution
class MT5Execution(ExecutionHandler):...
