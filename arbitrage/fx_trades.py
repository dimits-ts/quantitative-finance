import pandas as pd


class CurrencyTrade:
    """
    A record class to represent a currency trade.

    :param starting_currency: The currency to start with.
    :type starting_currency: str
    :param intermediate_currency: The currency to exchange to first.
    :type intermediate_currency: str
    :param end_currency: The final currency after the trade.
    :type end_currency: str
    :param arbitrage_rate: The arbitrage rate of the trade.
    :type arbitrage_rate: float
    """

    def __init__(self, starting_currency: str, intermediate_currency: str, end_currency: str, arbitrage_rate: float):
        """
        Initialize a CurrencyTrade record.

        :param starting_currency: The currency to start with.
        :type starting_currency: str
        :param intermediate_currency: The currency to exchange to first.
        :type intermediate_currency: str
        :param end_currency: The final currency after the trade.
        :type end_currency: str
        :param arbitrage_rate: The arbitrage rate of the trade.
        :type arbitrage_rate: float
        """
        self.starting_currency = starting_currency
        self.intermediate_currency = intermediate_currency
        self.end_currency = end_currency
        self.arbitrage_rate = arbitrage_rate

    def __str__(self):
        return f"{self.starting_currency}->{self.intermediate_currency}->{self.end_currency}: " \
               f"Arbitrage rate: {self.arbitrage_rate:.4f}"


def exchange_rate(quot_matrix: pd.DataFrame, from_currency: str, to_currency: str) -> float:
    """
    Get the exchange rate between two currencies.

    :param quot_matrix: The quotation matrix containing exchange rates.
    :type quot_matrix: pd.DataFrame
    :param from_currency: The currency to exchange from.
    :type from_currency: str
    :param to_currency: The currency to exchange to.
    :type to_currency: str
    :return: The exchange rate from `from_currency` to `to_currency`.
    :rtype: float
    """
    return quot_matrix.loc[from_currency, to_currency]


def trade_list_to_str(trades: list[CurrencyTrade]) -> str:
    """
    Returns a formatted string detailing a list of trades.
    :param trades: a list of currency trades
    :return: a string representation of the currency trades
    """
    return "\n".join([str(trade) for trade in trades])
